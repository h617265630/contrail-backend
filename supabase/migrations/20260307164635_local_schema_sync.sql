CREATE TYPE "public"."liketype" AS ENUM ('LIKE', 'LOVE', 'HAHA', 'WOW', 'SAD', 'ANGRY');

CREATE TYPE "public"."resourcetype" AS ENUM ('VIDEO', 'CLIP', 'link', 'document', 'article', 'video', 'clip');

CREATE SEQUENCE "public"."categories_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."docs_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."learning_path_comments_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."learning_paths_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."path_items_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."permissions_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."products_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."progress_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."resources_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."roles_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."subscriptions_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."user_files_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."user_images_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."users_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE SEQUENCE "public"."webhook_events_id_seq"
	AS integer
	INCREMENT BY 1
	MINVALUE 1 MAXVALUE 2147483647
	START WITH 1 CACHE 1 NO CYCLE
;

CREATE TABLE "public"."alembic_version" (
	"version_num" character varying(128) COLLATE "pg_catalog"."default" NOT NULL
);

CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num);

ALTER TABLE "public"."alembic_version" ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY USING INDEX "alembic_version_pkc";

CREATE TABLE "public"."articles" (
	"resource_id" integer NOT NULL,
	"publisher" character varying(255) COLLATE "pg_catalog"."default",
	"published_at" timestamp without time zone
);

CREATE UNIQUE INDEX articles_pkey ON public.articles USING btree (resource_id);

ALTER TABLE "public"."articles" ADD CONSTRAINT "articles_pkey" PRIMARY KEY USING INDEX "articles_pkey";

CREATE TABLE "public"."categories" (
	"id" integer DEFAULT nextval('categories_id_seq'::regclass) NOT NULL,
	"name" character varying(100) COLLATE "pg_catalog"."default" NOT NULL,
	"code" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"parent_id" integer,
	"level" integer,
	"description" text COLLATE "pg_catalog"."default",
	"is_leaf" boolean,
	"created_at" timestamp without time zone,
	"is_system" boolean DEFAULT true NOT NULL,
	"owner_user_id" integer
);

CREATE UNIQUE INDEX categories_pkey ON public.categories USING btree (id);

ALTER TABLE "public"."categories" ADD CONSTRAINT "categories_pkey" PRIMARY KEY USING INDEX "categories_pkey";

CREATE UNIQUE INDEX ix_categories_code ON public.categories USING btree (code);

CREATE INDEX ix_categories_id ON public.categories USING btree (id);

CREATE UNIQUE INDEX ix_categories_name ON public.categories USING btree (name);

ALTER TABLE "public"."categories" ADD CONSTRAINT "categories_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES categories(id) NOT VALID;

ALTER TABLE "public"."categories" VALIDATE CONSTRAINT "categories_parent_id_fkey";

ALTER SEQUENCE "public"."categories_id_seq" OWNED BY "public"."categories"."id";

CREATE TABLE "public"."docs" (
	"resource_id" integer NOT NULL,
	"doc_type" character varying(50) COLLATE "pg_catalog"."default",
	"version" character varying(50) COLLATE "pg_catalog"."default"
);

CREATE UNIQUE INDEX docs_pkey1 ON public.docs USING btree (resource_id);

ALTER TABLE "public"."docs" ADD CONSTRAINT "docs_pkey1" PRIMARY KEY USING INDEX "docs_pkey1";

CREATE TABLE "public"."docs_legacy" (
	"id" integer DEFAULT nextval('docs_id_seq'::regclass) NOT NULL,
	"name" character varying(100) COLLATE "pg_catalog"."default" NOT NULL,
	"description" text COLLATE "pg_catalog"."default"
);

CREATE UNIQUE INDEX docs_pkey ON public.docs_legacy USING btree (id);

ALTER TABLE "public"."docs_legacy" ADD CONSTRAINT "docs_pkey" PRIMARY KEY USING INDEX "docs_pkey";

CREATE INDEX ix_docs_id ON public.docs_legacy USING btree (id);

CREATE UNIQUE INDEX ix_docs_name ON public.docs_legacy USING btree (name);

ALTER SEQUENCE "public"."docs_id_seq" OWNED BY "public"."docs_legacy"."id";

CREATE TABLE "public"."learning_path_comments" (
	"id" integer DEFAULT nextval('learning_path_comments_id_seq'::regclass) NOT NULL,
	"learning_path_id" integer NOT NULL,
	"user_id" integer NOT NULL,
	"username" character varying(64) COLLATE "pg_catalog"."default" NOT NULL,
	"content" text COLLATE "pg_catalog"."default" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX learning_path_comments_pkey ON public.learning_path_comments USING btree (id);

ALTER TABLE "public"."learning_path_comments" ADD CONSTRAINT "learning_path_comments_pkey" PRIMARY KEY USING INDEX "learning_path_comments_pkey";

CREATE INDEX ix_learning_path_comments_id ON public.learning_path_comments USING btree (id);

CREATE INDEX ix_learning_path_comments_learning_path_id ON public.learning_path_comments USING btree (learning_path_id);

CREATE INDEX ix_learning_path_comments_user_id ON public.learning_path_comments USING btree (user_id);

ALTER SEQUENCE "public"."learning_path_comments_id_seq" OWNED BY "public"."learning_path_comments"."id";

CREATE TABLE "public"."learning_paths" (
	"id" integer DEFAULT nextval('learning_paths_id_seq'::regclass) NOT NULL,
	"title" character varying(200) COLLATE "pg_catalog"."default" NOT NULL,
	"description" text COLLATE "pg_catalog"."default",
	"is_public" boolean,
	"is_active" boolean,
	"category_id" integer NOT NULL,
	"cover_image_url" character varying(2048) COLLATE "pg_catalog"."default",
	"type" character varying(50) COLLATE "pg_catalog"."default"
);

ALTER TABLE "public"."learning_paths" ADD CONSTRAINT "fk_learning_paths_category_id_categories" FOREIGN KEY (category_id) REFERENCES categories(id) NOT VALID;

ALTER TABLE "public"."learning_paths" VALIDATE CONSTRAINT "fk_learning_paths_category_id_categories";

CREATE UNIQUE INDEX learning_paths_pkey ON public.learning_paths USING btree (id);

ALTER TABLE "public"."learning_paths" ADD CONSTRAINT "learning_paths_pkey" PRIMARY KEY USING INDEX "learning_paths_pkey";

CREATE INDEX ix_learning_paths_category_id ON public.learning_paths USING btree (category_id);

CREATE INDEX ix_learning_paths_id ON public.learning_paths USING btree (id);

ALTER TABLE "public"."learning_path_comments" ADD CONSTRAINT "learning_path_comments_learning_path_id_fkey" FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) NOT VALID;

ALTER TABLE "public"."learning_path_comments" VALIDATE CONSTRAINT "learning_path_comments_learning_path_id_fkey";

ALTER SEQUENCE "public"."learning_paths_id_seq" OWNED BY "public"."learning_paths"."id";

CREATE TABLE "public"."path_items" (
	"id" integer DEFAULT nextval('path_items_id_seq'::regclass) NOT NULL,
	"learning_path_id" integer NOT NULL,
	"resource_id" integer NOT NULL,
	"order_index" integer NOT NULL,
	"stage" character varying(100) COLLATE "pg_catalog"."default",
	"purpose" character varying(255) COLLATE "pg_catalog"."default",
	"estimated_time" integer,
	"is_optional" boolean DEFAULT false NOT NULL
);

ALTER TABLE "public"."path_items" ADD CONSTRAINT "path_items_learning_path_id_fkey" FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."path_items" VALIDATE CONSTRAINT "path_items_learning_path_id_fkey";

CREATE UNIQUE INDEX path_items_pkey ON public.path_items USING btree (id);

ALTER TABLE "public"."path_items" ADD CONSTRAINT "path_items_pkey" PRIMARY KEY USING INDEX "path_items_pkey";

CREATE UNIQUE INDEX uq_learning_path_order ON public.path_items USING btree (learning_path_id, order_index);

ALTER TABLE "public"."path_items" ADD CONSTRAINT "uq_learning_path_order" UNIQUE USING INDEX "uq_learning_path_order";

CREATE UNIQUE INDEX uq_learning_path_resource ON public.path_items USING btree (learning_path_id, resource_id);

ALTER TABLE "public"."path_items" ADD CONSTRAINT "uq_learning_path_resource" UNIQUE USING INDEX "uq_learning_path_resource";

CREATE INDEX ix_path_items_learning_path_id ON public.path_items USING btree (learning_path_id);

CREATE INDEX ix_path_items_resource_id ON public.path_items USING btree (resource_id);

ALTER SEQUENCE "public"."path_items_id_seq" OWNED BY "public"."path_items"."id";

CREATE TABLE "public"."permissions" (
	"id" integer DEFAULT nextval('permissions_id_seq'::regclass) NOT NULL,
	"name" character varying(100) COLLATE "pg_catalog"."default" NOT NULL,
	"code" character varying(100) COLLATE "pg_catalog"."default" NOT NULL,
	"description" text COLLATE "pg_catalog"."default",
	"module" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"action" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"is_active" boolean,
	"created_at" timestamp without time zone,
	"updated_at" timestamp without time zone
);

CREATE UNIQUE INDEX permissions_pkey ON public.permissions USING btree (id);

ALTER TABLE "public"."permissions" ADD CONSTRAINT "permissions_pkey" PRIMARY KEY USING INDEX "permissions_pkey";

CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code);

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);

ALTER SEQUENCE "public"."permissions_id_seq" OWNED BY "public"."permissions"."id";

CREATE TABLE "public"."products" (
	"id" integer DEFAULT nextval('products_id_seq'::regclass) NOT NULL,
	"name" character varying(100) COLLATE "pg_catalog"."default" NOT NULL,
	"description" text COLLATE "pg_catalog"."default"
);

CREATE UNIQUE INDEX products_pkey ON public.products USING btree (id);

ALTER TABLE "public"."products" ADD CONSTRAINT "products_pkey" PRIMARY KEY USING INDEX "products_pkey";

CREATE INDEX ix_products_id ON public.products USING btree (id);

CREATE UNIQUE INDEX ix_products_name ON public.products USING btree (name);

ALTER SEQUENCE "public"."products_id_seq" OWNED BY "public"."products"."id";

CREATE TABLE "public"."progress" (
	"id" integer DEFAULT nextval('progress_id_seq'::regclass) NOT NULL,
	"user_id" integer,
	"path_item_id" integer,
	"last_watched_time" timestamp without time zone,
	"progress_percentage" integer
);

ALTER TABLE "public"."progress" ADD CONSTRAINT "progress_path_item_id_fkey" FOREIGN KEY (path_item_id) REFERENCES path_items(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."progress" VALIDATE CONSTRAINT "progress_path_item_id_fkey";

CREATE UNIQUE INDEX progress_pkey ON public.progress USING btree (id);

ALTER TABLE "public"."progress" ADD CONSTRAINT "progress_pkey" PRIMARY KEY USING INDEX "progress_pkey";

ALTER SEQUENCE "public"."progress_id_seq" OWNED BY "public"."progress"."id";

CREATE TABLE "public"."resources" (
	"id" integer DEFAULT nextval('resources_id_seq'::regclass) NOT NULL,
	"resource_type" resourcetype NOT NULL,
	"platform" character varying(50) COLLATE "pg_catalog"."default",
	"title" character varying(200) COLLATE "pg_catalog"."default" NOT NULL,
	"summary" text COLLATE "pg_catalog"."default",
	"source_url" character varying(2048) COLLATE "pg_catalog"."default" NOT NULL,
	"thumbnail" character varying(1000) COLLATE "pg_catalog"."default",
	"difficulty" integer,
	"tags" json,
	"raw_meta" json,
	"created_at" timestamp without time zone DEFAULT now() NOT NULL,
	"category_id" integer NOT NULL,
	"is_system_public" boolean DEFAULT false NOT NULL,
	"community_score" integer DEFAULT 0 NOT NULL,
	"save_count" integer DEFAULT 0 NOT NULL,
	"trending_score" integer DEFAULT 0 NOT NULL
);

ALTER TABLE "public"."resources" ADD CONSTRAINT "fk_resources_category_id_categories" FOREIGN KEY (category_id) REFERENCES categories(id) NOT VALID;

ALTER TABLE "public"."resources" VALIDATE CONSTRAINT "fk_resources_category_id_categories";

CREATE UNIQUE INDEX resources_pkey ON public.resources USING btree (id);

ALTER TABLE "public"."resources" ADD CONSTRAINT "resources_pkey" PRIMARY KEY USING INDEX "resources_pkey";

CREATE INDEX ix_resources_category_id ON public.resources USING btree (category_id);

CREATE INDEX ix_resources_platform ON public.resources USING btree (platform);

CREATE INDEX ix_resources_resource_type ON public.resources USING btree (resource_type);

ALTER TABLE "public"."articles" ADD CONSTRAINT "articles_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."articles" VALIDATE CONSTRAINT "articles_resource_id_fkey";

ALTER TABLE "public"."docs" ADD CONSTRAINT "docs_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."docs" VALIDATE CONSTRAINT "docs_resource_id_fkey";

ALTER TABLE "public"."path_items" ADD CONSTRAINT "path_items_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."path_items" VALIDATE CONSTRAINT "path_items_resource_id_fkey";

ALTER SEQUENCE "public"."resources_id_seq" OWNED BY "public"."resources"."id";

CREATE TABLE "public"."role_permissions" (
	"role_id" integer NOT NULL,
	"permission_id" integer NOT NULL,
	"granted_at" timestamp without time zone
);

ALTER TABLE "public"."role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY (permission_id) REFERENCES permissions(id) NOT VALID;

ALTER TABLE "public"."role_permissions" VALIDATE CONSTRAINT "role_permissions_permission_id_fkey";

CREATE UNIQUE INDEX role_permissions_pkey ON public.role_permissions USING btree (role_id, permission_id);

ALTER TABLE "public"."role_permissions" ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY USING INDEX "role_permissions_pkey";

CREATE TABLE "public"."roles" (
	"id" integer DEFAULT nextval('roles_id_seq'::regclass) NOT NULL,
	"name" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"code" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"description" text COLLATE "pg_catalog"."default",
	"is_active" boolean,
	"is_system" boolean,
	"level" integer,
	"created_at" timestamp without time zone,
	"updated_at" timestamp without time zone
);

CREATE UNIQUE INDEX roles_pkey ON public.roles USING btree (id);

ALTER TABLE "public"."roles" ADD CONSTRAINT "roles_pkey" PRIMARY KEY USING INDEX "roles_pkey";

CREATE UNIQUE INDEX ix_roles_code ON public.roles USING btree (code);

CREATE INDEX ix_roles_id ON public.roles USING btree (id);

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);

ALTER TABLE "public"."role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY (role_id) REFERENCES roles(id) NOT VALID;

ALTER TABLE "public"."role_permissions" VALIDATE CONSTRAINT "role_permissions_role_id_fkey";

ALTER SEQUENCE "public"."roles_id_seq" OWNED BY "public"."roles"."id";

CREATE TABLE "public"."subscriptions" (
	"id" integer DEFAULT nextval('subscriptions_id_seq'::regclass) NOT NULL,
	"user_id" integer NOT NULL,
	"provider" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"provider_subscription_id" character varying(128) COLLATE "pg_catalog"."default",
	"plan_code" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"status" character varying(32) COLLATE "pg_catalog"."default" NOT NULL,
	"current_period_start" timestamp without time zone,
	"current_period_end" timestamp without time zone,
	"cancel_at_period_end" boolean NOT NULL,
	"created_at" timestamp without time zone,
	"updated_at" timestamp without time zone
);

CREATE UNIQUE INDEX subscriptions_pkey ON public.subscriptions USING btree (id);

ALTER TABLE "public"."subscriptions" ADD CONSTRAINT "subscriptions_pkey" PRIMARY KEY USING INDEX "subscriptions_pkey";

CREATE UNIQUE INDEX uq_subscription_user_provider ON public.subscriptions USING btree (user_id, provider);

ALTER TABLE "public"."subscriptions" ADD CONSTRAINT "uq_subscription_user_provider" UNIQUE USING INDEX "uq_subscription_user_provider";

CREATE INDEX ix_subscriptions_id ON public.subscriptions USING btree (id);

CREATE UNIQUE INDEX ix_subscriptions_provider_subscription_id ON public.subscriptions USING btree (provider_subscription_id);

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);

ALTER SEQUENCE "public"."subscriptions_id_seq" OWNED BY "public"."subscriptions"."id";

CREATE TABLE "public"."user_files" (
	"id" integer DEFAULT nextval('user_files_id_seq'::regclass) NOT NULL,
	"user_id" integer NOT NULL,
	"title" character varying(200) COLLATE "pg_catalog"."default",
	"file_type" character varying(20) COLLATE "pg_catalog"."default" NOT NULL,
	"original_filename" character varying(512) COLLATE "pg_catalog"."default",
	"content_type" character varying(200) COLLATE "pg_catalog"."default",
	"size_bytes" integer,
	"file_url" character varying(2048) COLLATE "pg_catalog"."default" NOT NULL,
	"created_at" timestamp without time zone,
	"content" text COLLATE "pg_catalog"."default"
);

CREATE UNIQUE INDEX user_files_pkey ON public.user_files USING btree (id);

ALTER TABLE "public"."user_files" ADD CONSTRAINT "user_files_pkey" PRIMARY KEY USING INDEX "user_files_pkey";

CREATE INDEX ix_user_files_id ON public.user_files USING btree (id);

CREATE INDEX ix_user_files_user_id ON public.user_files USING btree (user_id);

ALTER SEQUENCE "public"."user_files_id_seq" OWNED BY "public"."user_files"."id";

CREATE TABLE "public"."user_follows" (
	"follower_id" integer NOT NULL,
	"following_id" integer NOT NULL,
	"created_at" timestamp without time zone
);

CREATE UNIQUE INDEX user_follows_pkey ON public.user_follows USING btree (follower_id, following_id);

ALTER TABLE "public"."user_follows" ADD CONSTRAINT "user_follows_pkey" PRIMARY KEY USING INDEX "user_follows_pkey";

CREATE TABLE "public"."user_images" (
	"id" integer DEFAULT nextval('user_images_id_seq'::regclass) NOT NULL,
	"user_id" integer NOT NULL,
	"title" character varying(200) COLLATE "pg_catalog"."default",
	"image_url" character varying(2048) COLLATE "pg_catalog"."default" NOT NULL,
	"created_at" timestamp without time zone
);

CREATE UNIQUE INDEX user_images_pkey ON public.user_images USING btree (id);

ALTER TABLE "public"."user_images" ADD CONSTRAINT "user_images_pkey" PRIMARY KEY USING INDEX "user_images_pkey";

CREATE INDEX ix_user_images_id ON public.user_images USING btree (id);

CREATE INDEX ix_user_images_user_id ON public.user_images USING btree (user_id);

ALTER SEQUENCE "public"."user_images_id_seq" OWNED BY "public"."user_images"."id";

CREATE TABLE "public"."user_learning_paths" (
	"user_id" integer NOT NULL,
	"learning_path_id" integer NOT NULL
);

ALTER TABLE "public"."user_learning_paths" ADD CONSTRAINT "user_learning_paths_learning_path_id_fkey" FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) NOT VALID;

ALTER TABLE "public"."user_learning_paths" VALIDATE CONSTRAINT "user_learning_paths_learning_path_id_fkey";

CREATE UNIQUE INDEX user_learning_paths_pkey ON public.user_learning_paths USING btree (user_id, learning_path_id);

ALTER TABLE "public"."user_learning_paths" ADD CONSTRAINT "user_learning_paths_pkey" PRIMARY KEY USING INDEX "user_learning_paths_pkey";

CREATE TABLE "public"."user_resource" (
	"user_id" integer NOT NULL,
	"resource_id" integer NOT NULL,
	"created_at" timestamp without time zone DEFAULT now() NOT NULL,
	"is_public" boolean,
	"manual_weight" integer,
	"behavior_weight" integer,
	"effective_weight" integer,
	"added_at" timestamp without time zone,
	"last_opened" timestamp without time zone,
	"open_count" integer DEFAULT 0 NOT NULL,
	"completion_status" boolean DEFAULT false NOT NULL
);

ALTER TABLE "public"."user_resource" ADD CONSTRAINT "user_resource_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) NOT VALID;

ALTER TABLE "public"."user_resource" VALIDATE CONSTRAINT "user_resource_resource_id_fkey";

CREATE UNIQUE INDEX uq_user_resource ON public.user_resource USING btree (user_id, resource_id);

ALTER TABLE "public"."user_resource" ADD CONSTRAINT "uq_user_resource" PRIMARY KEY USING INDEX "uq_user_resource";

CREATE TABLE "public"."user_roles" (
	"user_id" integer NOT NULL,
	"role_id" integer NOT NULL,
	"assigned_at" timestamp without time zone
);

ALTER TABLE "public"."user_roles" ADD CONSTRAINT "user_roles_role_id_fkey" FOREIGN KEY (role_id) REFERENCES roles(id) NOT VALID;

ALTER TABLE "public"."user_roles" VALIDATE CONSTRAINT "user_roles_role_id_fkey";

CREATE UNIQUE INDEX user_roles_pkey ON public.user_roles USING btree (user_id, role_id);

ALTER TABLE "public"."user_roles" ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY USING INDEX "user_roles_pkey";

CREATE TABLE "public"."users" (
	"id" integer DEFAULT nextval('users_id_seq'::regclass) NOT NULL,
	"username" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"email" character varying(120) COLLATE "pg_catalog"."default" NOT NULL,
	"hashed_password" character varying(255) COLLATE "pg_catalog"."default" NOT NULL,
	"display_name" character varying(100) COLLATE "pg_catalog"."default",
	"avatar_url" character varying(500) COLLATE "pg_catalog"."default",
	"bio" text COLLATE "pg_catalog"."default",
	"created_at" timestamp without time zone,
	"updated_at" timestamp without time zone,
	"is_active" boolean,
	"is_superuser" boolean
);

CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id);

ALTER TABLE "public"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY USING INDEX "users_pkey";

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);

CREATE INDEX ix_users_id ON public.users USING btree (id);

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);

ALTER TABLE "public"."categories" ADD CONSTRAINT "fk_categories_owner_user_id_users" FOREIGN KEY (owner_user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."categories" VALIDATE CONSTRAINT "fk_categories_owner_user_id_users";

ALTER TABLE "public"."learning_path_comments" ADD CONSTRAINT "learning_path_comments_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."learning_path_comments" VALIDATE CONSTRAINT "learning_path_comments_user_id_fkey";

ALTER TABLE "public"."progress" ADD CONSTRAINT "progress_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."progress" VALIDATE CONSTRAINT "progress_user_id_fkey";

ALTER TABLE "public"."subscriptions" ADD CONSTRAINT "subscriptions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."subscriptions" VALIDATE CONSTRAINT "subscriptions_user_id_fkey";

ALTER TABLE "public"."user_files" ADD CONSTRAINT "user_files_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_files" VALIDATE CONSTRAINT "user_files_user_id_fkey";

ALTER TABLE "public"."user_follows" ADD CONSTRAINT "user_follows_follower_id_fkey" FOREIGN KEY (follower_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_follows" VALIDATE CONSTRAINT "user_follows_follower_id_fkey";

ALTER TABLE "public"."user_follows" ADD CONSTRAINT "user_follows_following_id_fkey" FOREIGN KEY (following_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_follows" VALIDATE CONSTRAINT "user_follows_following_id_fkey";

ALTER TABLE "public"."user_images" ADD CONSTRAINT "user_images_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_images" VALIDATE CONSTRAINT "user_images_user_id_fkey";

ALTER TABLE "public"."user_learning_paths" ADD CONSTRAINT "user_learning_paths_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_learning_paths" VALIDATE CONSTRAINT "user_learning_paths_user_id_fkey";

ALTER TABLE "public"."user_resource" ADD CONSTRAINT "user_resource_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_resource" VALIDATE CONSTRAINT "user_resource_user_id_fkey";

ALTER TABLE "public"."user_roles" ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

ALTER TABLE "public"."user_roles" VALIDATE CONSTRAINT "user_roles_user_id_fkey";

ALTER SEQUENCE "public"."users_id_seq" OWNED BY "public"."users"."id";

CREATE TABLE "public"."videos" (
	"resource_id" integer NOT NULL,
	"duration" integer,
	"channel" character varying(255) COLLATE "pg_catalog"."default",
	"video_id" character varying(100) COLLATE "pg_catalog"."default"
);

ALTER TABLE "public"."videos" ADD CONSTRAINT "videos_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE "public"."videos" VALIDATE CONSTRAINT "videos_resource_id_fkey";

CREATE UNIQUE INDEX videos_pkey ON public.videos USING btree (resource_id);

ALTER TABLE "public"."videos" ADD CONSTRAINT "videos_pkey" PRIMARY KEY USING INDEX "videos_pkey";

CREATE INDEX ix_videos_video_id ON public.videos USING btree (video_id);

CREATE TABLE "public"."webhook_events" (
	"id" integer DEFAULT nextval('webhook_events_id_seq'::regclass) NOT NULL,
	"provider" character varying(50) COLLATE "pg_catalog"."default" NOT NULL,
	"event_id" character varying(128) COLLATE "pg_catalog"."default",
	"event_type" character varying(128) COLLATE "pg_catalog"."default",
	"payload_json" text COLLATE "pg_catalog"."default" NOT NULL,
	"headers_json" text COLLATE "pg_catalog"."default" NOT NULL,
	"received_at" timestamp without time zone NOT NULL,
	"processed" boolean NOT NULL,
	"error" text COLLATE "pg_catalog"."default"
);

CREATE UNIQUE INDEX webhook_events_pkey ON public.webhook_events USING btree (id);

ALTER TABLE "public"."webhook_events" ADD CONSTRAINT "webhook_events_pkey" PRIMARY KEY USING INDEX "webhook_events_pkey";

CREATE INDEX ix_webhook_events_event_id ON public.webhook_events USING btree (event_id);

CREATE INDEX ix_webhook_events_event_type ON public.webhook_events USING btree (event_type);

CREATE INDEX ix_webhook_events_id ON public.webhook_events USING btree (id);

ALTER SEQUENCE "public"."webhook_events_id_seq" OWNED BY "public"."webhook_events"."id";

