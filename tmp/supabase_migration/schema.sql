--
-- PostgreSQL database dump
--

\restrict ZNPfef3Qg9YqJyR2hSNgGyaWsEnW63ixymVoTedhOwhekOHQpnfV9icLTaVPmyG

-- Dumped from database version 15.15
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY "public"."videos" DROP CONSTRAINT IF EXISTS "videos_resource_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_roles" DROP CONSTRAINT IF EXISTS "user_roles_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_roles" DROP CONSTRAINT IF EXISTS "user_roles_role_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_resource" DROP CONSTRAINT IF EXISTS "user_resource_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_resource" DROP CONSTRAINT IF EXISTS "user_resource_resource_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_learning_paths" DROP CONSTRAINT IF EXISTS "user_learning_paths_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_learning_paths" DROP CONSTRAINT IF EXISTS "user_learning_paths_learning_path_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_images" DROP CONSTRAINT IF EXISTS "user_images_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_follows" DROP CONSTRAINT IF EXISTS "user_follows_following_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_follows" DROP CONSTRAINT IF EXISTS "user_follows_follower_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."user_files" DROP CONSTRAINT IF EXISTS "user_files_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."subscriptions" DROP CONSTRAINT IF EXISTS "subscriptions_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."role_permissions" DROP CONSTRAINT IF EXISTS "role_permissions_role_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."role_permissions" DROP CONSTRAINT IF EXISTS "role_permissions_permission_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."progress" DROP CONSTRAINT IF EXISTS "progress_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."progress" DROP CONSTRAINT IF EXISTS "progress_path_item_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."path_items" DROP CONSTRAINT IF EXISTS "path_items_resource_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."path_items" DROP CONSTRAINT IF EXISTS "path_items_learning_path_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."learning_path_comments" DROP CONSTRAINT IF EXISTS "learning_path_comments_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."learning_path_comments" DROP CONSTRAINT IF EXISTS "learning_path_comments_learning_path_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."resources" DROP CONSTRAINT IF EXISTS "fk_resources_category_id_categories";
ALTER TABLE IF EXISTS ONLY "public"."learning_paths" DROP CONSTRAINT IF EXISTS "fk_learning_paths_category_id_categories";
ALTER TABLE IF EXISTS ONLY "public"."categories" DROP CONSTRAINT IF EXISTS "fk_categories_owner_user_id_users";
ALTER TABLE IF EXISTS ONLY "public"."docs" DROP CONSTRAINT IF EXISTS "docs_resource_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."categories" DROP CONSTRAINT IF EXISTS "categories_parent_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."articles" DROP CONSTRAINT IF EXISTS "articles_resource_id_fkey";
DROP INDEX IF EXISTS "public"."ix_webhook_events_id";
DROP INDEX IF EXISTS "public"."ix_webhook_events_event_type";
DROP INDEX IF EXISTS "public"."ix_webhook_events_event_id";
DROP INDEX IF EXISTS "public"."ix_videos_video_id";
DROP INDEX IF EXISTS "public"."ix_users_username";
DROP INDEX IF EXISTS "public"."ix_users_id";
DROP INDEX IF EXISTS "public"."ix_users_email";
DROP INDEX IF EXISTS "public"."ix_user_images_user_id";
DROP INDEX IF EXISTS "public"."ix_user_images_id";
DROP INDEX IF EXISTS "public"."ix_user_files_user_id";
DROP INDEX IF EXISTS "public"."ix_user_files_id";
DROP INDEX IF EXISTS "public"."ix_subscriptions_user_id";
DROP INDEX IF EXISTS "public"."ix_subscriptions_provider_subscription_id";
DROP INDEX IF EXISTS "public"."ix_subscriptions_id";
DROP INDEX IF EXISTS "public"."ix_roles_name";
DROP INDEX IF EXISTS "public"."ix_roles_id";
DROP INDEX IF EXISTS "public"."ix_roles_code";
DROP INDEX IF EXISTS "public"."ix_resources_resource_type";
DROP INDEX IF EXISTS "public"."ix_resources_platform";
DROP INDEX IF EXISTS "public"."ix_resources_category_id";
DROP INDEX IF EXISTS "public"."ix_products_name";
DROP INDEX IF EXISTS "public"."ix_products_id";
DROP INDEX IF EXISTS "public"."ix_permissions_name";
DROP INDEX IF EXISTS "public"."ix_permissions_id";
DROP INDEX IF EXISTS "public"."ix_permissions_code";
DROP INDEX IF EXISTS "public"."ix_path_items_resource_id";
DROP INDEX IF EXISTS "public"."ix_path_items_learning_path_id";
DROP INDEX IF EXISTS "public"."ix_learning_paths_id";
DROP INDEX IF EXISTS "public"."ix_learning_paths_category_id";
DROP INDEX IF EXISTS "public"."ix_learning_path_comments_user_id";
DROP INDEX IF EXISTS "public"."ix_learning_path_comments_learning_path_id";
DROP INDEX IF EXISTS "public"."ix_learning_path_comments_id";
DROP INDEX IF EXISTS "public"."ix_docs_name";
DROP INDEX IF EXISTS "public"."ix_docs_id";
DROP INDEX IF EXISTS "public"."ix_categories_name";
DROP INDEX IF EXISTS "public"."ix_categories_id";
DROP INDEX IF EXISTS "public"."ix_categories_code";
ALTER TABLE IF EXISTS ONLY "public"."webhook_events" DROP CONSTRAINT IF EXISTS "webhook_events_pkey";
ALTER TABLE IF EXISTS ONLY "public"."videos" DROP CONSTRAINT IF EXISTS "videos_pkey";
ALTER TABLE IF EXISTS ONLY "public"."users" DROP CONSTRAINT IF EXISTS "users_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_roles" DROP CONSTRAINT IF EXISTS "user_roles_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_learning_paths" DROP CONSTRAINT IF EXISTS "user_learning_paths_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_images" DROP CONSTRAINT IF EXISTS "user_images_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_follows" DROP CONSTRAINT IF EXISTS "user_follows_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_files" DROP CONSTRAINT IF EXISTS "user_files_pkey";
ALTER TABLE IF EXISTS ONLY "public"."user_resource" DROP CONSTRAINT IF EXISTS "uq_user_resource";
ALTER TABLE IF EXISTS ONLY "public"."subscriptions" DROP CONSTRAINT IF EXISTS "uq_subscription_user_provider";
ALTER TABLE IF EXISTS ONLY "public"."path_items" DROP CONSTRAINT IF EXISTS "uq_learning_path_resource";
ALTER TABLE IF EXISTS ONLY "public"."path_items" DROP CONSTRAINT IF EXISTS "uq_learning_path_order";
ALTER TABLE IF EXISTS ONLY "public"."subscriptions" DROP CONSTRAINT IF EXISTS "subscriptions_pkey";
ALTER TABLE IF EXISTS ONLY "public"."roles" DROP CONSTRAINT IF EXISTS "roles_pkey";
ALTER TABLE IF EXISTS ONLY "public"."role_permissions" DROP CONSTRAINT IF EXISTS "role_permissions_pkey";
ALTER TABLE IF EXISTS ONLY "public"."resources" DROP CONSTRAINT IF EXISTS "resources_pkey";
ALTER TABLE IF EXISTS ONLY "public"."progress" DROP CONSTRAINT IF EXISTS "progress_pkey";
ALTER TABLE IF EXISTS ONLY "public"."products" DROP CONSTRAINT IF EXISTS "products_pkey";
ALTER TABLE IF EXISTS ONLY "public"."permissions" DROP CONSTRAINT IF EXISTS "permissions_pkey";
ALTER TABLE IF EXISTS ONLY "public"."path_items" DROP CONSTRAINT IF EXISTS "path_items_pkey";
ALTER TABLE IF EXISTS ONLY "public"."learning_paths" DROP CONSTRAINT IF EXISTS "learning_paths_pkey";
ALTER TABLE IF EXISTS ONLY "public"."learning_path_comments" DROP CONSTRAINT IF EXISTS "learning_path_comments_pkey";
ALTER TABLE IF EXISTS ONLY "public"."docs" DROP CONSTRAINT IF EXISTS "docs_pkey1";
ALTER TABLE IF EXISTS ONLY "public"."docs_legacy" DROP CONSTRAINT IF EXISTS "docs_pkey";
ALTER TABLE IF EXISTS ONLY "public"."categories" DROP CONSTRAINT IF EXISTS "categories_pkey";
ALTER TABLE IF EXISTS ONLY "public"."articles" DROP CONSTRAINT IF EXISTS "articles_pkey";
ALTER TABLE IF EXISTS ONLY "public"."alembic_version" DROP CONSTRAINT IF EXISTS "alembic_version_pkc";
ALTER TABLE IF EXISTS "public"."webhook_events" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."users" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."user_images" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."user_files" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."subscriptions" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."roles" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."resources" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."progress" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."products" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."permissions" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."path_items" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."learning_paths" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."learning_path_comments" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."docs_legacy" ALTER COLUMN "id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."categories" ALTER COLUMN "id" DROP DEFAULT;
DROP SEQUENCE IF EXISTS "public"."webhook_events_id_seq";
DROP TABLE IF EXISTS "public"."webhook_events";
DROP TABLE IF EXISTS "public"."videos";
DROP SEQUENCE IF EXISTS "public"."users_id_seq";
DROP TABLE IF EXISTS "public"."users";
DROP TABLE IF EXISTS "public"."user_roles";
DROP TABLE IF EXISTS "public"."user_resource";
DROP TABLE IF EXISTS "public"."user_learning_paths";
DROP SEQUENCE IF EXISTS "public"."user_images_id_seq";
DROP TABLE IF EXISTS "public"."user_images";
DROP TABLE IF EXISTS "public"."user_follows";
DROP SEQUENCE IF EXISTS "public"."user_files_id_seq";
DROP TABLE IF EXISTS "public"."user_files";
DROP SEQUENCE IF EXISTS "public"."subscriptions_id_seq";
DROP TABLE IF EXISTS "public"."subscriptions";
DROP SEQUENCE IF EXISTS "public"."roles_id_seq";
DROP TABLE IF EXISTS "public"."roles";
DROP TABLE IF EXISTS "public"."role_permissions";
DROP SEQUENCE IF EXISTS "public"."resources_id_seq";
DROP TABLE IF EXISTS "public"."resources";
DROP SEQUENCE IF EXISTS "public"."progress_id_seq";
DROP TABLE IF EXISTS "public"."progress";
DROP SEQUENCE IF EXISTS "public"."products_id_seq";
DROP TABLE IF EXISTS "public"."products";
DROP SEQUENCE IF EXISTS "public"."permissions_id_seq";
DROP TABLE IF EXISTS "public"."permissions";
DROP SEQUENCE IF EXISTS "public"."path_items_id_seq";
DROP TABLE IF EXISTS "public"."path_items";
DROP SEQUENCE IF EXISTS "public"."learning_paths_id_seq";
DROP TABLE IF EXISTS "public"."learning_paths";
DROP SEQUENCE IF EXISTS "public"."learning_path_comments_id_seq";
DROP TABLE IF EXISTS "public"."learning_path_comments";
DROP SEQUENCE IF EXISTS "public"."docs_id_seq";
DROP TABLE IF EXISTS "public"."docs_legacy";
DROP TABLE IF EXISTS "public"."docs";
DROP SEQUENCE IF EXISTS "public"."categories_id_seq";
DROP TABLE IF EXISTS "public"."categories";
DROP TABLE IF EXISTS "public"."articles";
DROP TABLE IF EXISTS "public"."alembic_version";
DROP TYPE IF EXISTS "public"."resourcetype";
DROP TYPE IF EXISTS "public"."liketype";
--
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- Name: liketype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."liketype" AS ENUM (
    'LIKE',
    'LOVE',
    'HAHA',
    'WOW',
    'SAD',
    'ANGRY'
);


--
-- Name: resourcetype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."resourcetype" AS ENUM (
    'VIDEO',
    'CLIP',
    'link',
    'document',
    'article',
    'video',
    'clip'
);


SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(128) NOT NULL
);


--
-- Name: articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."articles" (
    "resource_id" integer NOT NULL,
    "publisher" character varying(255),
    "published_at" timestamp without time zone
);


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."categories" (
    "id" integer NOT NULL,
    "name" character varying(100) NOT NULL,
    "code" character varying(50) NOT NULL,
    "parent_id" integer,
    "level" integer,
    "description" "text",
    "is_leaf" boolean,
    "created_at" timestamp without time zone,
    "is_system" boolean DEFAULT true NOT NULL,
    "owner_user_id" integer
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."categories_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."categories_id_seq" OWNED BY "public"."categories"."id";


--
-- Name: docs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."docs" (
    "resource_id" integer NOT NULL,
    "doc_type" character varying(50),
    "version" character varying(50)
);


--
-- Name: docs_legacy; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."docs_legacy" (
    "id" integer NOT NULL,
    "name" character varying(100) NOT NULL,
    "description" "text"
);


--
-- Name: docs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."docs_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: docs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."docs_id_seq" OWNED BY "public"."docs_legacy"."id";


--
-- Name: learning_path_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."learning_path_comments" (
    "id" integer NOT NULL,
    "learning_path_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "username" character varying(64) NOT NULL,
    "content" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."learning_path_comments_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."learning_path_comments_id_seq" OWNED BY "public"."learning_path_comments"."id";


--
-- Name: learning_paths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."learning_paths" (
    "id" integer NOT NULL,
    "title" character varying(200) NOT NULL,
    "description" "text",
    "is_public" boolean,
    "is_active" boolean,
    "category_id" integer NOT NULL,
    "cover_image_url" character varying(2048),
    "type" character varying(50)
);


--
-- Name: learning_paths_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."learning_paths_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: learning_paths_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."learning_paths_id_seq" OWNED BY "public"."learning_paths"."id";


--
-- Name: path_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."path_items" (
    "id" integer NOT NULL,
    "learning_path_id" integer NOT NULL,
    "resource_id" integer NOT NULL,
    "order_index" integer NOT NULL,
    "stage" character varying(100),
    "purpose" character varying(255),
    "estimated_time" integer,
    "is_optional" boolean DEFAULT false NOT NULL
);


--
-- Name: path_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."path_items_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: path_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."path_items_id_seq" OWNED BY "public"."path_items"."id";


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."permissions" (
    "id" integer NOT NULL,
    "name" character varying(100) NOT NULL,
    "code" character varying(100) NOT NULL,
    "description" "text",
    "module" character varying(50) NOT NULL,
    "action" character varying(50) NOT NULL,
    "is_active" boolean,
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone
);


--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."permissions_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."permissions_id_seq" OWNED BY "public"."permissions"."id";


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."products" (
    "id" integer NOT NULL,
    "name" character varying(100) NOT NULL,
    "description" "text"
);


--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."products_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."products_id_seq" OWNED BY "public"."products"."id";


--
-- Name: progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."progress" (
    "id" integer NOT NULL,
    "user_id" integer,
    "path_item_id" integer,
    "last_watched_time" timestamp without time zone,
    "progress_percentage" integer
);


--
-- Name: progress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."progress_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."progress_id_seq" OWNED BY "public"."progress"."id";


--
-- Name: resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."resources" (
    "id" integer NOT NULL,
    "resource_type" "public"."resourcetype" NOT NULL,
    "platform" character varying(50),
    "title" character varying(200) NOT NULL,
    "summary" "text",
    "source_url" character varying(2048) NOT NULL,
    "thumbnail" character varying(1000),
    "difficulty" integer,
    "tags" "json",
    "raw_meta" "json",
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "category_id" integer NOT NULL,
    "is_system_public" boolean DEFAULT false NOT NULL,
    "community_score" integer DEFAULT 0 NOT NULL,
    "save_count" integer DEFAULT 0 NOT NULL,
    "trending_score" integer DEFAULT 0 NOT NULL
);


--
-- Name: resources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."resources_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."resources_id_seq" OWNED BY "public"."resources"."id";


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."role_permissions" (
    "role_id" integer NOT NULL,
    "permission_id" integer NOT NULL,
    "granted_at" timestamp without time zone
);


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."roles" (
    "id" integer NOT NULL,
    "name" character varying(50) NOT NULL,
    "code" character varying(50) NOT NULL,
    "description" "text",
    "is_active" boolean,
    "is_system" boolean,
    "level" integer,
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."roles_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."roles_id_seq" OWNED BY "public"."roles"."id";


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."subscriptions" (
    "id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "provider" character varying(50) NOT NULL,
    "provider_subscription_id" character varying(128),
    "plan_code" character varying(50) NOT NULL,
    "status" character varying(32) NOT NULL,
    "current_period_start" timestamp without time zone,
    "current_period_end" timestamp without time zone,
    "cancel_at_period_end" boolean NOT NULL,
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone
);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."subscriptions_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."subscriptions_id_seq" OWNED BY "public"."subscriptions"."id";


--
-- Name: user_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_files" (
    "id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "title" character varying(200),
    "file_type" character varying(20) NOT NULL,
    "original_filename" character varying(512),
    "content_type" character varying(200),
    "size_bytes" integer,
    "file_url" character varying(2048) NOT NULL,
    "created_at" timestamp without time zone,
    "content" "text"
);


--
-- Name: user_files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."user_files_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."user_files_id_seq" OWNED BY "public"."user_files"."id";


--
-- Name: user_follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_follows" (
    "follower_id" integer NOT NULL,
    "following_id" integer NOT NULL,
    "created_at" timestamp without time zone
);


--
-- Name: user_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_images" (
    "id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "title" character varying(200),
    "image_url" character varying(2048) NOT NULL,
    "created_at" timestamp without time zone
);


--
-- Name: user_images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."user_images_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."user_images_id_seq" OWNED BY "public"."user_images"."id";


--
-- Name: user_learning_paths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_learning_paths" (
    "user_id" integer NOT NULL,
    "learning_path_id" integer NOT NULL
);


--
-- Name: user_resource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_resource" (
    "user_id" integer NOT NULL,
    "resource_id" integer NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "is_public" boolean,
    "manual_weight" integer,
    "behavior_weight" integer,
    "effective_weight" integer,
    "added_at" timestamp without time zone,
    "last_opened" timestamp without time zone,
    "open_count" integer DEFAULT 0 NOT NULL,
    "completion_status" boolean DEFAULT false NOT NULL
);


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."user_roles" (
    "user_id" integer NOT NULL,
    "role_id" integer NOT NULL,
    "assigned_at" timestamp without time zone
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."users" (
    "id" integer NOT NULL,
    "username" character varying(50) NOT NULL,
    "email" character varying(120) NOT NULL,
    "hashed_password" character varying(255) NOT NULL,
    "display_name" character varying(100),
    "avatar_url" character varying(500),
    "bio" "text",
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone,
    "is_active" boolean,
    "is_superuser" boolean
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."users_id_seq" OWNED BY "public"."users"."id";


--
-- Name: videos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."videos" (
    "resource_id" integer NOT NULL,
    "duration" integer,
    "channel" character varying(255),
    "video_id" character varying(100)
);


--
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."webhook_events" (
    "id" integer NOT NULL,
    "provider" character varying(50) NOT NULL,
    "event_id" character varying(128),
    "event_type" character varying(128),
    "payload_json" "text" NOT NULL,
    "headers_json" "text" NOT NULL,
    "received_at" timestamp without time zone NOT NULL,
    "processed" boolean NOT NULL,
    "error" "text"
);


--
-- Name: webhook_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."webhook_events_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: webhook_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."webhook_events_id_seq" OWNED BY "public"."webhook_events"."id";


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."categories_id_seq"'::"regclass");


--
-- Name: docs_legacy id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."docs_legacy" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."docs_id_seq"'::"regclass");


--
-- Name: learning_path_comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_path_comments" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."learning_path_comments_id_seq"'::"regclass");


--
-- Name: learning_paths id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_paths" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."learning_paths_id_seq"'::"regclass");


--
-- Name: path_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."path_items_id_seq"'::"regclass");


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."permissions" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."permissions_id_seq"'::"regclass");


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."products" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."products_id_seq"'::"regclass");


--
-- Name: progress id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."progress" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."progress_id_seq"'::"regclass");


--
-- Name: resources id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."resources" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."resources_id_seq"'::"regclass");


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."roles" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."roles_id_seq"'::"regclass");


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."subscriptions" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."subscriptions_id_seq"'::"regclass");


--
-- Name: user_files id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_files" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."user_files_id_seq"'::"regclass");


--
-- Name: user_images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_images" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."user_images_id_seq"'::"regclass");


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."users" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."users_id_seq"'::"regclass");


--
-- Name: webhook_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."webhook_events" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."webhook_events_id_seq"'::"regclass");


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."alembic_version"
    ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."articles"
    ADD CONSTRAINT "articles_pkey" PRIMARY KEY ("resource_id");


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_pkey" PRIMARY KEY ("id");


--
-- Name: docs_legacy docs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."docs_legacy"
    ADD CONSTRAINT "docs_pkey" PRIMARY KEY ("id");


--
-- Name: docs docs_pkey1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."docs"
    ADD CONSTRAINT "docs_pkey1" PRIMARY KEY ("resource_id");


--
-- Name: learning_path_comments learning_path_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_path_comments"
    ADD CONSTRAINT "learning_path_comments_pkey" PRIMARY KEY ("id");


--
-- Name: learning_paths learning_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_paths"
    ADD CONSTRAINT "learning_paths_pkey" PRIMARY KEY ("id");


--
-- Name: path_items path_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items"
    ADD CONSTRAINT "path_items_pkey" PRIMARY KEY ("id");


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."permissions"
    ADD CONSTRAINT "permissions_pkey" PRIMARY KEY ("id");


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."products"
    ADD CONSTRAINT "products_pkey" PRIMARY KEY ("id");


--
-- Name: progress progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."progress"
    ADD CONSTRAINT "progress_pkey" PRIMARY KEY ("id");


--
-- Name: resources resources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."resources"
    ADD CONSTRAINT "resources_pkey" PRIMARY KEY ("id");


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id", "permission_id");


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."roles"
    ADD CONSTRAINT "roles_pkey" PRIMARY KEY ("id");


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "subscriptions_pkey" PRIMARY KEY ("id");


--
-- Name: path_items uq_learning_path_order; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items"
    ADD CONSTRAINT "uq_learning_path_order" UNIQUE ("learning_path_id", "order_index");


--
-- Name: path_items uq_learning_path_resource; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items"
    ADD CONSTRAINT "uq_learning_path_resource" UNIQUE ("learning_path_id", "resource_id");


--
-- Name: subscriptions uq_subscription_user_provider; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "uq_subscription_user_provider" UNIQUE ("user_id", "provider");


--
-- Name: user_resource uq_user_resource; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_resource"
    ADD CONSTRAINT "uq_user_resource" PRIMARY KEY ("user_id", "resource_id");


--
-- Name: user_files user_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_files"
    ADD CONSTRAINT "user_files_pkey" PRIMARY KEY ("id");


--
-- Name: user_follows user_follows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_follows"
    ADD CONSTRAINT "user_follows_pkey" PRIMARY KEY ("follower_id", "following_id");


--
-- Name: user_images user_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_images"
    ADD CONSTRAINT "user_images_pkey" PRIMARY KEY ("id");


--
-- Name: user_learning_paths user_learning_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_learning_paths"
    ADD CONSTRAINT "user_learning_paths_pkey" PRIMARY KEY ("user_id", "learning_path_id");


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id", "role_id");


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."videos"
    ADD CONSTRAINT "videos_pkey" PRIMARY KEY ("resource_id");


--
-- Name: webhook_events webhook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."webhook_events"
    ADD CONSTRAINT "webhook_events_pkey" PRIMARY KEY ("id");


--
-- Name: ix_categories_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_categories_code" ON "public"."categories" USING "btree" ("code");


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_categories_id" ON "public"."categories" USING "btree" ("id");


--
-- Name: ix_categories_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_categories_name" ON "public"."categories" USING "btree" ("name");


--
-- Name: ix_docs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_docs_id" ON "public"."docs_legacy" USING "btree" ("id");


--
-- Name: ix_docs_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_docs_name" ON "public"."docs_legacy" USING "btree" ("name");


--
-- Name: ix_learning_path_comments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_learning_path_comments_id" ON "public"."learning_path_comments" USING "btree" ("id");


--
-- Name: ix_learning_path_comments_learning_path_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_learning_path_comments_learning_path_id" ON "public"."learning_path_comments" USING "btree" ("learning_path_id");


--
-- Name: ix_learning_path_comments_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_learning_path_comments_user_id" ON "public"."learning_path_comments" USING "btree" ("user_id");


--
-- Name: ix_learning_paths_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_learning_paths_category_id" ON "public"."learning_paths" USING "btree" ("category_id");


--
-- Name: ix_learning_paths_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_learning_paths_id" ON "public"."learning_paths" USING "btree" ("id");


--
-- Name: ix_path_items_learning_path_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_path_items_learning_path_id" ON "public"."path_items" USING "btree" ("learning_path_id");


--
-- Name: ix_path_items_resource_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_path_items_resource_id" ON "public"."path_items" USING "btree" ("resource_id");


--
-- Name: ix_permissions_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_permissions_code" ON "public"."permissions" USING "btree" ("code");


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_permissions_id" ON "public"."permissions" USING "btree" ("id");


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_permissions_name" ON "public"."permissions" USING "btree" ("name");


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_products_id" ON "public"."products" USING "btree" ("id");


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_products_name" ON "public"."products" USING "btree" ("name");


--
-- Name: ix_resources_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_resources_category_id" ON "public"."resources" USING "btree" ("category_id");


--
-- Name: ix_resources_platform; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_resources_platform" ON "public"."resources" USING "btree" ("platform");


--
-- Name: ix_resources_resource_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_resources_resource_type" ON "public"."resources" USING "btree" ("resource_type");


--
-- Name: ix_roles_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_roles_code" ON "public"."roles" USING "btree" ("code");


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_roles_id" ON "public"."roles" USING "btree" ("id");


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_roles_name" ON "public"."roles" USING "btree" ("name");


--
-- Name: ix_subscriptions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_subscriptions_id" ON "public"."subscriptions" USING "btree" ("id");


--
-- Name: ix_subscriptions_provider_subscription_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_subscriptions_provider_subscription_id" ON "public"."subscriptions" USING "btree" ("provider_subscription_id");


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_subscriptions_user_id" ON "public"."subscriptions" USING "btree" ("user_id");


--
-- Name: ix_user_files_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_user_files_id" ON "public"."user_files" USING "btree" ("id");


--
-- Name: ix_user_files_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_user_files_user_id" ON "public"."user_files" USING "btree" ("user_id");


--
-- Name: ix_user_images_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_user_images_id" ON "public"."user_images" USING "btree" ("id");


--
-- Name: ix_user_images_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_user_images_user_id" ON "public"."user_images" USING "btree" ("user_id");


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_users_email" ON "public"."users" USING "btree" ("email");


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_users_id" ON "public"."users" USING "btree" ("id");


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_users_username" ON "public"."users" USING "btree" ("username");


--
-- Name: ix_videos_video_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_videos_video_id" ON "public"."videos" USING "btree" ("video_id");


--
-- Name: ix_webhook_events_event_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_webhook_events_event_id" ON "public"."webhook_events" USING "btree" ("event_id");


--
-- Name: ix_webhook_events_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_webhook_events_event_type" ON "public"."webhook_events" USING "btree" ("event_type");


--
-- Name: ix_webhook_events_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_webhook_events_id" ON "public"."webhook_events" USING "btree" ("id");


--
-- Name: articles articles_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."articles"
    ADD CONSTRAINT "articles_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id") ON DELETE CASCADE;


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."categories"("id");


--
-- Name: docs docs_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."docs"
    ADD CONSTRAINT "docs_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id") ON DELETE CASCADE;


--
-- Name: categories fk_categories_owner_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "fk_categories_owner_user_id_users" FOREIGN KEY ("owner_user_id") REFERENCES "public"."users"("id");


--
-- Name: learning_paths fk_learning_paths_category_id_categories; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_paths"
    ADD CONSTRAINT "fk_learning_paths_category_id_categories" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");


--
-- Name: resources fk_resources_category_id_categories; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."resources"
    ADD CONSTRAINT "fk_resources_category_id_categories" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");


--
-- Name: learning_path_comments learning_path_comments_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_path_comments"
    ADD CONSTRAINT "learning_path_comments_learning_path_id_fkey" FOREIGN KEY ("learning_path_id") REFERENCES "public"."learning_paths"("id");


--
-- Name: learning_path_comments learning_path_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."learning_path_comments"
    ADD CONSTRAINT "learning_path_comments_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: path_items path_items_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items"
    ADD CONSTRAINT "path_items_learning_path_id_fkey" FOREIGN KEY ("learning_path_id") REFERENCES "public"."learning_paths"("id") ON DELETE CASCADE;


--
-- Name: path_items path_items_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."path_items"
    ADD CONSTRAINT "path_items_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id") ON DELETE CASCADE;


--
-- Name: progress progress_path_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."progress"
    ADD CONSTRAINT "progress_path_item_id_fkey" FOREIGN KEY ("path_item_id") REFERENCES "public"."path_items"("id") ON DELETE CASCADE;


--
-- Name: progress progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."progress"
    ADD CONSTRAINT "progress_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."permissions"("id");


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."role_permissions"
    ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."roles"("id");


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."subscriptions"
    ADD CONSTRAINT "subscriptions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: user_files user_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_files"
    ADD CONSTRAINT "user_files_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: user_follows user_follows_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_follows"
    ADD CONSTRAINT "user_follows_follower_id_fkey" FOREIGN KEY ("follower_id") REFERENCES "public"."users"("id");


--
-- Name: user_follows user_follows_following_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_follows"
    ADD CONSTRAINT "user_follows_following_id_fkey" FOREIGN KEY ("following_id") REFERENCES "public"."users"("id");


--
-- Name: user_images user_images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_images"
    ADD CONSTRAINT "user_images_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: user_learning_paths user_learning_paths_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_learning_paths"
    ADD CONSTRAINT "user_learning_paths_learning_path_id_fkey" FOREIGN KEY ("learning_path_id") REFERENCES "public"."learning_paths"("id");


--
-- Name: user_learning_paths user_learning_paths_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_learning_paths"
    ADD CONSTRAINT "user_learning_paths_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: user_resource user_resource_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_resource"
    ADD CONSTRAINT "user_resource_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id");


--
-- Name: user_resource user_resource_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_resource"
    ADD CONSTRAINT "user_resource_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."roles"("id");


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."user_roles"
    ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- Name: videos videos_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."videos"
    ADD CONSTRAINT "videos_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id") ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict ZNPfef3Qg9YqJyR2hSNgGyaWsEnW63ixymVoTedhOwhekOHQpnfV9icLTaVPmyG

