--
-- PostgreSQL database dump
--

\restrict CYPwxxR2fqg7UEeOgM8TWTky1N4827chEQ93UlKYLbyqdusBAYx1pFefpuotf2Y

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

ALTER TABLE IF EXISTS ONLY public.videos DROP CONSTRAINT IF EXISTS videos_resource_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_role_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_resource DROP CONSTRAINT IF EXISTS user_resource_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_resource DROP CONSTRAINT IF EXISTS user_resource_resource_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_learning_paths DROP CONSTRAINT IF EXISTS user_learning_paths_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_learning_paths DROP CONSTRAINT IF EXISTS user_learning_paths_learning_path_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_images DROP CONSTRAINT IF EXISTS user_images_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_follows DROP CONSTRAINT IF EXISTS user_follows_following_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_follows DROP CONSTRAINT IF EXISTS user_follows_follower_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_files DROP CONSTRAINT IF EXISTS user_files_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.role_permissions DROP CONSTRAINT IF EXISTS role_permissions_role_id_fkey;
ALTER TABLE IF EXISTS ONLY public.role_permissions DROP CONSTRAINT IF EXISTS role_permissions_permission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.progress DROP CONSTRAINT IF EXISTS progress_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.progress DROP CONSTRAINT IF EXISTS progress_path_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.path_items DROP CONSTRAINT IF EXISTS path_items_resource_id_fkey;
ALTER TABLE IF EXISTS ONLY public.path_items DROP CONSTRAINT IF EXISTS path_items_learning_path_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learning_path_comments DROP CONSTRAINT IF EXISTS learning_path_comments_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learning_path_comments DROP CONSTRAINT IF EXISTS learning_path_comments_learning_path_id_fkey;
ALTER TABLE IF EXISTS ONLY public.resources DROP CONSTRAINT IF EXISTS fk_resources_category_id_categories;
ALTER TABLE IF EXISTS ONLY public.learning_paths DROP CONSTRAINT IF EXISTS fk_learning_paths_category_id_categories;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS fk_categories_owner_user_id_users;
ALTER TABLE IF EXISTS ONLY public.docs DROP CONSTRAINT IF EXISTS docs_resource_id_fkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.articles DROP CONSTRAINT IF EXISTS articles_resource_id_fkey;
DROP INDEX IF EXISTS public.ix_webhook_events_id;
DROP INDEX IF EXISTS public.ix_webhook_events_event_type;
DROP INDEX IF EXISTS public.ix_webhook_events_event_id;
DROP INDEX IF EXISTS public.ix_videos_video_id;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_user_images_user_id;
DROP INDEX IF EXISTS public.ix_user_images_id;
DROP INDEX IF EXISTS public.ix_user_files_user_id;
DROP INDEX IF EXISTS public.ix_user_files_id;
DROP INDEX IF EXISTS public.ix_subscriptions_user_id;
DROP INDEX IF EXISTS public.ix_subscriptions_provider_subscription_id;
DROP INDEX IF EXISTS public.ix_subscriptions_id;
DROP INDEX IF EXISTS public.ix_roles_name;
DROP INDEX IF EXISTS public.ix_roles_id;
DROP INDEX IF EXISTS public.ix_roles_code;
DROP INDEX IF EXISTS public.ix_resources_resource_type;
DROP INDEX IF EXISTS public.ix_resources_platform;
DROP INDEX IF EXISTS public.ix_resources_category_id;
DROP INDEX IF EXISTS public.ix_products_name;
DROP INDEX IF EXISTS public.ix_products_id;
DROP INDEX IF EXISTS public.ix_permissions_name;
DROP INDEX IF EXISTS public.ix_permissions_id;
DROP INDEX IF EXISTS public.ix_permissions_code;
DROP INDEX IF EXISTS public.ix_path_items_resource_id;
DROP INDEX IF EXISTS public.ix_path_items_learning_path_id;
DROP INDEX IF EXISTS public.ix_learning_paths_id;
DROP INDEX IF EXISTS public.ix_learning_paths_category_id;
DROP INDEX IF EXISTS public.ix_learning_path_comments_user_id;
DROP INDEX IF EXISTS public.ix_learning_path_comments_learning_path_id;
DROP INDEX IF EXISTS public.ix_learning_path_comments_id;
DROP INDEX IF EXISTS public.ix_docs_name;
DROP INDEX IF EXISTS public.ix_docs_id;
DROP INDEX IF EXISTS public.ix_categories_name;
DROP INDEX IF EXISTS public.ix_categories_id;
DROP INDEX IF EXISTS public.ix_categories_code;
ALTER TABLE IF EXISTS ONLY public.webhook_events DROP CONSTRAINT IF EXISTS webhook_events_pkey;
ALTER TABLE IF EXISTS ONLY public.videos DROP CONSTRAINT IF EXISTS videos_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_pkey;
ALTER TABLE IF EXISTS ONLY public.user_learning_paths DROP CONSTRAINT IF EXISTS user_learning_paths_pkey;
ALTER TABLE IF EXISTS ONLY public.user_images DROP CONSTRAINT IF EXISTS user_images_pkey;
ALTER TABLE IF EXISTS ONLY public.user_follows DROP CONSTRAINT IF EXISTS user_follows_pkey;
ALTER TABLE IF EXISTS ONLY public.user_files DROP CONSTRAINT IF EXISTS user_files_pkey;
ALTER TABLE IF EXISTS ONLY public.user_resource DROP CONSTRAINT IF EXISTS uq_user_resource;
ALTER TABLE IF EXISTS ONLY public.subscriptions DROP CONSTRAINT IF EXISTS uq_subscription_user_provider;
ALTER TABLE IF EXISTS ONLY public.path_items DROP CONSTRAINT IF EXISTS uq_learning_path_resource;
ALTER TABLE IF EXISTS ONLY public.path_items DROP CONSTRAINT IF EXISTS uq_learning_path_order;
ALTER TABLE IF EXISTS ONLY public.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_pkey;
ALTER TABLE IF EXISTS ONLY public.roles DROP CONSTRAINT IF EXISTS roles_pkey;
ALTER TABLE IF EXISTS ONLY public.role_permissions DROP CONSTRAINT IF EXISTS role_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.resources DROP CONSTRAINT IF EXISTS resources_pkey;
ALTER TABLE IF EXISTS ONLY public.progress DROP CONSTRAINT IF EXISTS progress_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE IF EXISTS ONLY public.permissions DROP CONSTRAINT IF EXISTS permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.path_items DROP CONSTRAINT IF EXISTS path_items_pkey;
ALTER TABLE IF EXISTS ONLY public.learning_paths DROP CONSTRAINT IF EXISTS learning_paths_pkey;
ALTER TABLE IF EXISTS ONLY public.learning_path_comments DROP CONSTRAINT IF EXISTS learning_path_comments_pkey;
ALTER TABLE IF EXISTS ONLY public.docs DROP CONSTRAINT IF EXISTS docs_pkey1;
ALTER TABLE IF EXISTS ONLY public.docs_legacy DROP CONSTRAINT IF EXISTS docs_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS ONLY public.articles DROP CONSTRAINT IF EXISTS articles_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.webhook_events ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_images ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_files ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.subscriptions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.roles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.resources ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.progress ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.products ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.path_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.learning_paths ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.learning_path_comments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.docs_legacy ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.webhook_events_id_seq;
DROP TABLE IF EXISTS public.webhook_events;
DROP TABLE IF EXISTS public.videos;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.user_roles;
DROP TABLE IF EXISTS public.user_resource;
DROP TABLE IF EXISTS public.user_learning_paths;
DROP SEQUENCE IF EXISTS public.user_images_id_seq;
DROP TABLE IF EXISTS public.user_images;
DROP TABLE IF EXISTS public.user_follows;
DROP SEQUENCE IF EXISTS public.user_files_id_seq;
DROP TABLE IF EXISTS public.user_files;
DROP SEQUENCE IF EXISTS public.subscriptions_id_seq;
DROP TABLE IF EXISTS public.subscriptions;
DROP SEQUENCE IF EXISTS public.roles_id_seq;
DROP TABLE IF EXISTS public.roles;
DROP TABLE IF EXISTS public.role_permissions;
DROP SEQUENCE IF EXISTS public.resources_id_seq;
DROP TABLE IF EXISTS public.resources;
DROP SEQUENCE IF EXISTS public.progress_id_seq;
DROP TABLE IF EXISTS public.progress;
DROP SEQUENCE IF EXISTS public.products_id_seq;
DROP TABLE IF EXISTS public.products;
DROP SEQUENCE IF EXISTS public.permissions_id_seq;
DROP TABLE IF EXISTS public.permissions;
DROP SEQUENCE IF EXISTS public.path_items_id_seq;
DROP TABLE IF EXISTS public.path_items;
DROP SEQUENCE IF EXISTS public.learning_paths_id_seq;
DROP TABLE IF EXISTS public.learning_paths;
DROP SEQUENCE IF EXISTS public.learning_path_comments_id_seq;
DROP TABLE IF EXISTS public.learning_path_comments;
DROP SEQUENCE IF EXISTS public.docs_id_seq;
DROP TABLE IF EXISTS public.docs_legacy;
DROP TABLE IF EXISTS public.docs;
DROP SEQUENCE IF EXISTS public.categories_id_seq;
DROP TABLE IF EXISTS public.categories;
DROP TABLE IF EXISTS public.articles;
DROP TABLE IF EXISTS public.alembic_version;
DROP TYPE IF EXISTS public.resourcetype;
DROP TYPE IF EXISTS public.liketype;
--
-- Name: liketype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.liketype AS ENUM (
    'LIKE',
    'LOVE',
    'HAHA',
    'WOW',
    'SAD',
    'ANGRY'
);


ALTER TYPE public.liketype OWNER TO postgres;

--
-- Name: resourcetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.resourcetype AS ENUM (
    'VIDEO',
    'CLIP',
    'link',
    'document',
    'article',
    'video',
    'clip'
);


ALTER TYPE public.resourcetype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(128) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.articles (
    resource_id integer NOT NULL,
    publisher character varying(255),
    published_at timestamp without time zone
);


ALTER TABLE public.articles OWNER TO postgres;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    parent_id integer,
    level integer,
    description text,
    is_leaf boolean,
    created_at timestamp without time zone,
    is_system boolean DEFAULT true NOT NULL,
    owner_user_id integer
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: docs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.docs (
    resource_id integer NOT NULL,
    doc_type character varying(50),
    version character varying(50)
);


ALTER TABLE public.docs OWNER TO postgres;

--
-- Name: docs_legacy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.docs_legacy (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.docs_legacy OWNER TO postgres;

--
-- Name: docs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.docs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.docs_id_seq OWNER TO postgres;

--
-- Name: docs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.docs_id_seq OWNED BY public.docs_legacy.id;


--
-- Name: learning_path_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.learning_path_comments (
    id integer NOT NULL,
    learning_path_id integer NOT NULL,
    user_id integer NOT NULL,
    username character varying(64) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.learning_path_comments OWNER TO postgres;

--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.learning_path_comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.learning_path_comments_id_seq OWNER TO postgres;

--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.learning_path_comments_id_seq OWNED BY public.learning_path_comments.id;


--
-- Name: learning_paths; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.learning_paths (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    is_public boolean,
    is_active boolean,
    category_id integer NOT NULL,
    cover_image_url character varying(2048),
    type character varying(50)
);


ALTER TABLE public.learning_paths OWNER TO postgres;

--
-- Name: learning_paths_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.learning_paths_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.learning_paths_id_seq OWNER TO postgres;

--
-- Name: learning_paths_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.learning_paths_id_seq OWNED BY public.learning_paths.id;


--
-- Name: path_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.path_items (
    id integer NOT NULL,
    learning_path_id integer NOT NULL,
    resource_id integer NOT NULL,
    order_index integer NOT NULL,
    stage character varying(100),
    purpose character varying(255),
    estimated_time integer,
    is_optional boolean DEFAULT false NOT NULL
);


ALTER TABLE public.path_items OWNER TO postgres;

--
-- Name: path_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.path_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.path_items_id_seq OWNER TO postgres;

--
-- Name: path_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.path_items_id_seq OWNED BY public.path_items.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(100) NOT NULL,
    description text,
    module character varying(50) NOT NULL,
    action character varying(50) NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: progress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.progress (
    id integer NOT NULL,
    user_id integer,
    path_item_id integer,
    last_watched_time timestamp without time zone,
    progress_percentage integer
);


ALTER TABLE public.progress OWNER TO postgres;

--
-- Name: progress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.progress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.progress_id_seq OWNER TO postgres;

--
-- Name: progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.progress_id_seq OWNED BY public.progress.id;


--
-- Name: resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resources (
    id integer NOT NULL,
    resource_type public.resourcetype NOT NULL,
    platform character varying(50),
    title character varying(200) NOT NULL,
    summary text,
    source_url character varying(2048) NOT NULL,
    thumbnail character varying(1000),
    difficulty integer,
    tags json,
    raw_meta json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    category_id integer NOT NULL,
    is_system_public boolean DEFAULT false NOT NULL,
    community_score integer DEFAULT 0 NOT NULL,
    save_count integer DEFAULT 0 NOT NULL,
    trending_score integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.resources OWNER TO postgres;

--
-- Name: resources_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resources_id_seq OWNER TO postgres;

--
-- Name: resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resources_id_seq OWNED BY public.resources.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL,
    granted_at timestamp without time zone
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    is_active boolean,
    is_system boolean,
    level integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_subscription_id character varying(128),
    plan_code character varying(50) NOT NULL,
    status character varying(32) NOT NULL,
    current_period_start timestamp without time zone,
    current_period_end timestamp without time zone,
    cancel_at_period_end boolean NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: user_files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_files (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(200),
    file_type character varying(20) NOT NULL,
    original_filename character varying(512),
    content_type character varying(200),
    size_bytes integer,
    file_url character varying(2048) NOT NULL,
    created_at timestamp without time zone,
    content text
);


ALTER TABLE public.user_files OWNER TO postgres;

--
-- Name: user_files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_files_id_seq OWNER TO postgres;

--
-- Name: user_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_files_id_seq OWNED BY public.user_files.id;


--
-- Name: user_follows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_follows (
    follower_id integer NOT NULL,
    following_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.user_follows OWNER TO postgres;

--
-- Name: user_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_images (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(200),
    image_url character varying(2048) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.user_images OWNER TO postgres;

--
-- Name: user_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_images_id_seq OWNER TO postgres;

--
-- Name: user_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_images_id_seq OWNED BY public.user_images.id;


--
-- Name: user_learning_paths; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_learning_paths (
    user_id integer NOT NULL,
    learning_path_id integer NOT NULL
);


ALTER TABLE public.user_learning_paths OWNER TO postgres;

--
-- Name: user_resource; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_resource (
    user_id integer NOT NULL,
    resource_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    is_public boolean,
    manual_weight integer,
    behavior_weight integer,
    effective_weight integer,
    added_at timestamp without time zone,
    last_opened timestamp without time zone,
    open_count integer DEFAULT 0 NOT NULL,
    completion_status boolean DEFAULT false NOT NULL
);


ALTER TABLE public.user_resource OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_at timestamp without time zone
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    display_name character varying(100),
    avatar_url character varying(500),
    bio text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean,
    is_superuser boolean
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos (
    resource_id integer NOT NULL,
    duration integer,
    channel character varying(255),
    video_id character varying(100)
);


ALTER TABLE public.videos OWNER TO postgres;

--
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webhook_events (
    id integer NOT NULL,
    provider character varying(50) NOT NULL,
    event_id character varying(128),
    event_type character varying(128),
    payload_json text NOT NULL,
    headers_json text NOT NULL,
    received_at timestamp without time zone NOT NULL,
    processed boolean NOT NULL,
    error text
);


ALTER TABLE public.webhook_events OWNER TO postgres;

--
-- Name: webhook_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.webhook_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.webhook_events_id_seq OWNER TO postgres;

--
-- Name: webhook_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.webhook_events_id_seq OWNED BY public.webhook_events.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: docs_legacy id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.docs_legacy ALTER COLUMN id SET DEFAULT nextval('public.docs_id_seq'::regclass);


--
-- Name: learning_path_comments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_path_comments ALTER COLUMN id SET DEFAULT nextval('public.learning_path_comments_id_seq'::regclass);


--
-- Name: learning_paths id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_paths ALTER COLUMN id SET DEFAULT nextval('public.learning_paths_id_seq'::regclass);


--
-- Name: path_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items ALTER COLUMN id SET DEFAULT nextval('public.path_items_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: progress id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progress ALTER COLUMN id SET DEFAULT nextval('public.progress_id_seq'::regclass);


--
-- Name: resources id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources ALTER COLUMN id SET DEFAULT nextval('public.resources_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: user_files id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_files ALTER COLUMN id SET DEFAULT nextval('public.user_files_id_seq'::regclass);


--
-- Name: user_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_images ALTER COLUMN id SET DEFAULT nextval('public.user_images_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: webhook_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_events ALTER COLUMN id SET DEFAULT nextval('public.webhook_events_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20260208_0001
\.


--
-- Data for Name: articles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.articles (resource_id, publisher, published_at) FROM stdin;
12	\N	\N
14	\N	\N
15	\N	\N
32	\N	\N
33	\N	\N
34	\N	\N
50	\N	\N
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name, code, parent_id, level, description, is_leaf, created_at, is_system, owner_user_id) FROM stdin;
1	AI	ai	\N	0	\N	t	2026-01-17 01:30:32.899845	t	\N
2	设计	design	\N	0	\N	t	2026-01-17 01:30:32.899847	t	\N
3	UI	ui	\N	0	\N	t	2026-01-17 01:30:32.899847	t	\N
4	前端	frontend	\N	0	\N	t	2026-01-17 01:30:32.899848	t	\N
5	后端	backend	\N	0	\N	t	2026-01-17 01:30:32.899849	t	\N
6	手工	handmade	\N	0	\N	t	2026-01-17 01:30:32.899849	t	\N
7	其他	other	\N	0	\N	t	2026-01-17 01:30:32.89985	t	\N
15	🚀 Business & Productivity	business_productivity	\N	0	🚀 Business & Productivity category	f	2026-02-24 19:16:25.955109	t	\N
16	Startups	startups	15	1	Startups category	t	2026-02-24 19:16:25.963261	t	\N
17	Entrepreneurship	entrepreneurship	15	1	Entrepreneurship category	t	2026-02-24 19:16:25.964321	t	\N
18	Marketing	marketing	15	1	Marketing category	t	2026-02-24 19:16:25.964946	t	\N
19	Finance	finance	15	1	Finance category	t	2026-02-24 19:16:25.966119	t	\N
20	Productivity	productivity	15	1	Productivity category	t	2026-02-24 19:16:25.966847	t	\N
21	Remote Work	remote_work	15	1	Remote Work category	t	2026-02-24 19:16:25.967632	t	\N
22	🏠 Lifestyle	lifestyle	\N	0	🏠 Lifestyle category	f	2026-02-24 19:16:25.968366	t	\N
23	Home Decor	home_decor	22	1	Home Decor category	t	2026-02-24 19:16:25.968962	t	\N
24	Organization	organization	22	1	Organization category	t	2026-02-24 19:16:25.96942	t	\N
25	Minimalism	minimalism	22	1	Minimalism category	t	2026-02-24 19:16:25.969845	t	\N
26	Travel	travel	22	1	Travel category	t	2026-02-24 19:16:25.97027	t	\N
27	Wellness	wellness	22	1	Wellness category	t	2026-02-24 19:16:25.970687	t	\N
28	Fitness	fitness	22	1	Fitness category	t	2026-02-24 19:16:25.971084	t	\N
29	🍳 Food & Cooking	food_cooking	\N	0	🍳 Food & Cooking category	f	2026-02-24 19:16:25.971492	t	\N
30	Recipes	recipes	29	1	Recipes category	t	2026-02-24 19:16:25.971883	t	\N
31	Baking	baking	29	1	Baking category	t	2026-02-24 19:16:25.97226	t	\N
32	Healthy eating	healthy_eating	29	1	Healthy eating category	t	2026-02-24 19:16:25.972985	t	\N
33	Meal prep	meal_prep	29	1	Meal prep category	t	2026-02-24 19:16:25.973565	t	\N
34	🎮 Entertainment	entertainment	\N	0	🎮 Entertainment category	f	2026-02-24 19:16:25.974313	t	\N
35	Gaming	gaming	34	1	Gaming category	t	2026-02-24 19:16:25.974891	t	\N
36	Movies	movies	34	1	Movies category	t	2026-02-24 19:16:25.975589	t	\N
37	Anime	anime	34	1	Anime category	t	2026-02-24 19:16:25.976605	t	\N
38	Music	music	34	1	Music category	t	2026-02-24 19:16:25.97846	t	\N
39	Pop Culture	pop_culture	34	1	Pop Culture category	t	2026-02-24 19:16:25.980796	t	\N
40	🧠 Personal Development	personal_development	\N	0	🧠 Personal Development category	f	2026-02-24 19:16:25.982044	t	\N
41	Habits	habits	40	1	Habits category	t	2026-02-24 19:16:25.982916	t	\N
42	Psychology	psychology	40	1	Psychology category	t	2026-02-24 19:16:25.983622	t	\N
43	Motivation	motivation	40	1	Motivation category	t	2026-02-24 19:16:25.984446	t	\N
\.


--
-- Data for Name: docs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.docs (resource_id, doc_type, version) FROM stdin;
13	\N	\N
26	\N	\N
27	\N	\N
28	\N	\N
29	\N	\N
39	\N	\N
40	\N	\N
41	\N	\N
42	\N	\N
43	\N	\N
44	\N	\N
45	\N	\N
46	\N	\N
60	\N	\N
61	\N	\N
\.


--
-- Data for Name: docs_legacy; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.docs_legacy (id, name, description) FROM stdin;
\.


--
-- Data for Name: learning_path_comments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.learning_path_comments (id, learning_path_id, user_id, username, content, created_at) FROM stdin;
\.


--
-- Data for Name: learning_paths; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.learning_paths (id, title, description, is_public, is_active, category_id, cover_image_url, type) FROM stdin;
7	flutter应用	一个flutter	t	t	2	https://i.ytimg.com/vi/VyR8nqD3sQ8/hqdefault.jpg	\N
3	My Path 8yo4ug	desc	f	t	7	\N	\N
17	github 相关项目	123	t	t	2	https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432	\N
18	linear path	123	t	t	3	https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432	linear path
19	stuctured path	123	t	t	5	https://opengraph.githubassets.com/5a3dde964e04ec495a6a46b857bd8b20f32030f43d18df41067b6c412c0171ad/openai/gpt-3	partical pool
20	partical pool	partical'	t	t	3	https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw	partical pool
21	stucted	123	t	t	7	https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw	structured path
22	GitHub Trends Weekly	Track GitHub Trending weekly: shortlist repos, read READMEs, capture key ideas, and turn them into an actionable learning path.	t	t	7	https://i.ytimg.com/vi/98EZwfObm-o/hqdefault.jpg	linear path
23	GitHub Trends Weekly	Track GitHub Trending weekly: shortlist repos, read READMEs, capture key ideas, and turn them into an actionable learning path.	t	t	5	https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg	linear path
\.


--
-- Data for Name: path_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.path_items (id, learning_path_id, resource_id, order_index, stage, purpose, estimated_time, is_optional) FROM stdin;
2	7	17	1	\N	\N	\N	f
3	7	16	2	\N	\N	\N	f
4	7	15	3	\N	\N	\N	f
5	7	14	4	\N	\N	\N	f
6	7	13	5	\N	\N	\N	f
10	17	28	1	\N	\N	\N	f
11	18	28	1	\N	\N	\N	f
12	19	26	1	\N	\N	\N	f
13	20	29	1	\N	\N	\N	f
14	21	29	1	\N	\N	\N	f
15	22	38	1	\N	\N	\N	f
16	22	39	2	\N	\N	\N	f
17	23	59	1	\N	\N	\N	f
18	23	58	2	\N	\N	\N	f
19	23	60	3	\N	\N	\N	f
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, name, code, description, module, action, is_active, created_at, updated_at) FROM stdin;
1	查看用户	user.read	\N	user	read	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
2	创建用户	user.create	\N	user	create	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
3	更新用户	user.update	\N	user	update	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
4	删除用户	user.delete	\N	user	delete	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
5	管理用户角色	user.role.manage	\N	user	role_manage	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
6	查看角色	role.read	\N	role	read	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
7	创建角色	role.create	\N	role	create	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
8	更新角色	role.update	\N	role	update	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
9	删除角色	role.delete	\N	role	delete	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
10	查看权限	permission.read	\N	permission	read	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
11	创建权限	permission.create	\N	permission	create	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
12	更新权限	permission.update	\N	permission	update	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
13	删除权限	permission.delete	\N	permission	delete	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
14	查看视频	video.read	\N	video	read	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
15	上传视频	video.upload	\N	video	upload	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
16	编辑视频	video.update	\N	video	update	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
17	删除视频	video.delete	\N	video	delete	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
18	查看剪辑	clip.read	\N	clip	read	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
19	创建剪辑	clip.create	\N	clip	create	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
20	编辑剪辑	clip.update	\N	clip	update	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
21	删除剪辑	clip.delete	\N	clip	delete	t	2026-01-10 17:30:29.570029	2026-01-10 17:30:29.570029
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, name, description) FROM stdin;
\.


--
-- Data for Name: progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.progress (id, user_id, path_item_id, last_watched_time, progress_percentage) FROM stdin;
3	9	19	2026-02-12 07:24:43.428048	95
\.


--
-- Data for Name: resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resources (id, resource_type, platform, title, summary, source_url, thumbnail, difficulty, tags, raw_meta, created_at, category_id, is_system_public, community_score, save_count, trending_score) FROM stdin;
11	video	xiaohongshu	【测试】小红书视频资源	这是一个来自小红书的测试视频资源	https://www.xiaohongshu.com/explore/65a1b2c3d4e5f6g7h8i9j0k1	https://sns-img-qc.xhscdn.com/test.jpg	\N	{}	{}	2026-01-26 06:40:43.871616	1	f	0	0	0
12	article	medium	【测试】Understanding Machine Learning Basics	A comprehensive guide to machine learning fundamentals	https://medium.com/@example/understanding-machine-learning-basics-123abc	https://miro.medium.com/max/test.jpg	\N	{}	{}	2026-01-26 06:40:43.872837	1	f	0	0	0
13	document	github	【测试】OpenAI GPT-3 Repository	Official repository for GPT-3 documentation and examples	https://github.com/openai/gpt-3	https://opengraph.githubassets.com/test.png	\N	{}	{}	2026-01-26 06:40:43.87513	1	f	0	0	0
14	article	medium	【测试】Deep Learning Explained	An in-depth explanation of deep learning concepts and applications	https://medium.com/@techwriter/deep-learning-explained-456def	https://miro.medium.com/max/test2.jpg	\N	{}	{}	2026-01-26 06:40:43.876591	1	f	0	0	0
15	article	barackobama.medium.com	a-wake-up-call-for-every-american-ec0115195303	\N	https://barackobama.medium.com/a-wake-up-call-for-every-american-ec0115195303	\N	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-01-26 06:43:24.576788	6	f	0	0	0
16	video	youtube	Relaxing Work Music | Zen Workspace Nordic Chill for Deep Concentration	\N	https://www.youtube.com/watch?v=HQiMFS9eTYk&list=RDHQiMFS9eTYk&start_radio=1	https://i.ytimg.com/vi/HQiMFS9eTYk/hqdefault.jpg	\N	{}	{"author": "StillMind Music", "publish_date": null, "video_id": "HQiMFS9eTYk", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-01-26 06:47:08.835216	1	f	0	0	0
17	video	youtube	【PEACEFUL PIANO BGM】一聽就能讓你放鬆！90分鐘的沉浸式舒壓旋律，溫柔的琴聲會撫平你的煩躁，陪你度過輕鬆又平靜的時光。特別適合用來冥想、放鬆，還有學習和工作時當背景音樂	\N	https://www.youtube.com/watch?v=q18spKfNYaw	https://i.ytimg.com/vi/q18spKfNYaw/hqdefault.jpg	\N	{}	{"author": "FM RELAXING WORLD", "publish_date": null, "video_id": "q18spKfNYaw", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-01-26 06:48:19.55493	5	f	0	0	0
18	video	bilibili	【2026最全面ComfyUI教程】B站强推！建议所有想学ComfyUI的同学，死磕这条视频，花了一周时间整理的ComfyUI零基础入门教程！_哔哩哔哩_bilibili	【2026最全面ComfyUI教程】B站强推！建议所有想学ComfyUI的同学，死磕这条视频，花了一周时间整理的ComfyUI零基础入门教程！共计11条视频，包括：【Comfyui教程】2026最新中文版comfyui终极整合包、【Comfyui教程】第1节 课程概览与ComfyUI的优势、【Comfyui教程】第2节 ComfyUI界面导览与最基础生图流程等，UP主更多精彩视频，请关注UP账号。	https://www.bilibili.com/video/BV1pNvsBfEad/?spm_id_from=333.1007.tianma.1-1-1.click	//i2.hdslb.com/bfs/archive/6da151b1eebb5ac8ff6c9c343d916acd6bb829cb.jpg@100w_100h_1c.png	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "video", "og_video": null, "twitter_player": null}	2026-01-26 06:58:51.567546	7	f	0	0	0
19	video	xiaohongshu	野兽先生生日拿出50万抽奖给订阅的粉丝 - 小红书	#野兽先生 #全网猎形行动 #野兽先生最新 #超自然行动组 #喜剧打开生活的另一面 #kpl #红薯地偶遇Rihanna #红薯地造梦师 #野生vlogger成长计划 #人生的意义	https://www.xiaohongshu.com/explore/6975d66e000000002203af20?xsec_token=ABys3qRV_zjUoTdTbuENMJwtVCp4SZ2PLT4FWzoQzWRG4=&xsec_source=pc_feed	\N	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-01-26 07:00:10.772724	7	f	0	0	0
26	document	github	GitHub - openai/gpt-3: GPT-3: Language Models are Few-Shot Learners	GPT-3: Language Models are Few-Shot Learners. Contribute to openai/gpt-3 development by creating an account on GitHub.	https://github.com/openai/gpt-3	https://opengraph.githubassets.com/5a3dde964e04ec495a6a46b857bd8b20f32030f43d18df41067b6c412c0171ad/openai/gpt-3	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-01-26 07:38:57.350378	7	f	0	0	0
29	document	github	GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞	Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞  - GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞	https://github.com/openclaw/openclaw	https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-01-31 02:52:21.47365	7	f	0	0	0
30	video	youtube	這個角度拍到 Luka 的出手真的太扯了	\N	https://youtube.com/shorts/TUH7dgFlp0k?si=ie2tpN_uWpPmJrta	https://i.ytimg.com/vi/TUH7dgFlp0k/hq2.jpg	\N	{}	{"author": "Pe Score", "publish_date": null, "video_id": "TUH7dgFlp0k", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-01 06:25:07.733948	7	f	0	0	0
31	video	youtube	Claude Code 从 0 到 1 全攻略 —— MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理/ 后台任务 / 权限 ......	\N	https://www.youtube.com/watch?v=AT4b9kLtQCQ	https://i.ytimg.com/vi/AT4b9kLtQCQ/hqdefault.jpg	\N	{}	{"author": "\\u9a6c\\u514b\\u7684\\u6280\\u672f\\u5de5\\u4f5c\\u574a", "publish_date": null, "video_id": "AT4b9kLtQCQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-01 06:27:29.996726	7	f	0	0	0
32	article	docs.clawd.bot	Setup - OpenClaw	\N	https://docs.clawd.bot/start/setup	https://clawdhub.mintlify.app/mintlify-assets/_next/image?url=%2F_mintlify%2Fapi%2Fog%3Fdivision%3DStart%2BHere%26title%3DSetup%26logoLight%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26logoDark%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26primaryColor%3D%2523FF5A36%26backgroundLight%3D%2523ffffff%26backgroundDark%3D%25230a0d0d&w=1200&q=100	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}	2026-02-01 06:42:11.745299	7	f	0	0	0
33	article	skillsmp.com	nextlevelbuilder-ui-ux-pro-max-skill-claude-skills-ui-ux-pro-max-skill-md	\N	https://skillsmp.com/zh/skills/nextlevelbuilder-ui-ux-pro-max-skill-claude-skills-ui-ux-pro-max-skill-md	\N	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-01 06:43:02.160636	7	f	0	0	0
47	video	chatgpt.com	ChatGPT - 原生家庭与突破	ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster.	https://chatgpt.com/share/6987ab9a-d6d4-800b-b068-39723021952a	https://cdn.openai.com/chatgpt/share-og.png	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-08 05:17:21.053052	7	f	0	1	0
48	video	youtube	Deep Focus Coding Music: Chillstep for Coding, Work & Study	\N	https://www.youtube.com/watch?v=yNAFtADhzss&list=RDyNAFtADhzss&start_radio=1	https://i.ytimg.com/vi/yNAFtADhzss/hqdefault.jpg	\N	{}	{"author": "Focusphere", "publish_date": null, "video_id": "yNAFtADhzss", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-08 05:23:59.097342	7	f	0	1	0
49	video	youtube	【100% 無廣告 ,輕音樂】一播放就進入心流狀態的極度專注讀書音樂 - 學習/閱讀/工作/放鬆音樂	\N	https://www.youtube.com/watch?v=bVLRxsjM-jQ&list=RDbVLRxsjM-jQ&start_radio=1	https://i.ytimg.com/vi/bVLRxsjM-jQ/hqdefault.jpg	\N	{}	{"author": "Healing & Meditation", "publish_date": null, "video_id": "bVLRxsjM-jQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-08 05:52:28.721279	7	f	0	1	0
50	article	ui.shadcn.com	New Project - shadcn/ui	Customize everything. Pick your component library, icons, base color, theme, fonts and create your own version of shadcn/ui.	https://ui.shadcn.com/create?item=vercel	https://ui.shadcn.com/og.jpg	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}	2026-02-09 05:22:04.223548	7	f	0	1	0
27	document	github	GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞	Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞  - GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞	https://github.com/moltbot/moltbot	https://opengraph.githubassets.com/bca4deae4eb50f3ca8ac4603fd665a13f98883fbb48af0791b33d6d11950c932/openclaw/openclaw	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-01-31 02:48:56.376963	7	f	0	1	0
34	article	docs.openclaw.ai	OpenClaw - OpenClaw	\N	https://docs.openclaw.ai/	https://clawdhub.mintlify.app/mintlify-assets/_next/image?url=%2F_mintlify%2Fapi%2Fog%3Fdivision%3DStart%2BHere%26title%3DOpenClaw%26logoLight%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26logoDark%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26primaryColor%3D%2523FF5A36%26backgroundLight%3D%2523ffffff%26backgroundDark%3D%25230a0d0d&w=1200&q=100	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}	2026-02-01 06:43:57.739971	7	f	0	0	0
35	video	youtube	Agent 的概念、原理与构建模式 —— 从零打造一个简化版的 Claude Code	\N	https://www.youtube.com/watch?v=GE0pFiFJTKo	https://i.ytimg.com/vi/GE0pFiFJTKo/hqdefault.jpg	\N	{}	{"author": "\\u9a6c\\u514b\\u7684\\u6280\\u672f\\u5de5\\u4f5c\\u574a", "publish_date": null, "video_id": "GE0pFiFJTKo", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-07 00:03:13.801234	1	f	0	0	0
38	video	youtube	【香蜜回忆杀】萨顶顶在环球综艺秀里面一首《左手指月》惊艳全场，耳朵怀孕了	\N	https://www.youtube.com/watch?v=98EZwfObm-o&list=RD98EZwfObm-o&start_radio=1	https://i.ytimg.com/vi/98EZwfObm-o/hqdefault.jpg	\N	{}	{"author": "\\u660e\\u661f\\u60c5\\u62a5\\u5c40Celebrity Intelligence Agency", "publish_date": null, "video_id": "98EZwfObm-o", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-07 02:26:58.655737	7	f	0	0	0
39	document	github	GitHub - Vanessa219/vditor: ♏ 一款浏览器端的 Markdown 编辑器，支持所见即所得（富文本）、即时渲染（类似 Typora）和分屏预览模式。An In-browser Markdown editor, support WYSIWYG (Rich Text), Instant Rendering (Typora-like) and Split View modes.	♏  一款浏览器端的 Markdown 编辑器，支持所见即所得（富文本）、即时渲染（类似 Typora）和分屏预览模式。An In-browser Markdown editor, support WYSIWYG (Rich Text),  Instant Rendering (Typora-like) and Split View modes. - Vanessa219/vditor	https://github.com/Vanessa219/vditor	https://opengraph.githubassets.com/9c26857d3b61e501e83907a3401d468d57f91ce4c25566bc3a6d097c71dbaa47/Vanessa219/vditor	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:14:05.687279	7	f	0	0	0
40	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:19:08.319082	1	f	0	0	0
41	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:19:36.68228	1	f	0	0	0
42	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:19:46.28529	7	f	0	0	0
43	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:20:00.585549	1	f	0	0	0
46	document	github	GitHub - fengdu78/Coursera-ML-AndrewNg-Notes: 吴恩达老师的机器学习课程个人笔记	吴恩达老师的机器学习课程个人笔记. Contribute to fengdu78/Coursera-ML-AndrewNg-Notes development by creating an account on GitHub.	https://github.com/fengdu78/Coursera-ML-AndrewNg-Notes	https://opengraph.githubassets.com/7709ceddf6e41c7229705b9084595f56c8df9903b7d6c627d740ea20f8f60290/fengdu78/Coursera-ML-AndrewNg-Notes	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:25:09.938532	7	f	0	0	0
45	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:24:04.310906	6	f	0	1	0
51	video	x.com	2020914244330324177	\N	https://x.com/EHuanglu/status/2020914244330324177?s=20	\N	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-10 18:22:17.595864	7	f	0	1	0
52	video	x.com	2020914244330324177	\N	https://x.com/EHuanglu/status/2020914244330324177?s=20	\N	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-10 18:22:49.871084	7	f	0	1	0
53	video	x	Overtime: Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq	Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq	https://x.com/overtime/status/2020939399203258718?s=20	https://pbs.twimg.com/amplify_video_thumb/2020939344056352770/img/JzBxAJgSEKqnOU5m.jpg	\N	{}	{"author": "Overtime", "publish_date": "2026-02-09", "video_id": "2020939399203258718", "duration_seconds": null, "chapters": [], "og_type": "video.other", "og_video": "https://video.twimg.com/amplify_video/2020939344056352770/vid/avc1/720x1280/87QH_gaJglZgXvs1.mp4?tag=21", "twitter_player": null}	2026-02-10 20:29:54.455913	7	f	0	1	0
28	document	github	GitHub - nextlevelbuilder/ui-ux-pro-max-skill: An AI SKILL that provide design intelligence for building professional UI/UX multiple platforms	An AI SKILL that provide design intelligence for building professional UI/UX multiple platforms - nextlevelbuilder/ui-ux-pro-max-skill	https://github.com/nextlevelbuilder/ui-ux-pro-max-skill	https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-01-31 02:51:04.49539	7	f	0	1	0
54	video	youtube	【100% 無廣告 ,輕音樂】一播放就進入心流狀態的極度專注讀書音樂 - 學習/閱讀/工作/放鬆音樂	在這個節奏越來越快、壓力無處不在的世界裡，我們都需要一段真正安靜、沒有打擾、沒有廣告的時光，讓心慢慢沉靜下來，重新找回專注、平衡與內在的平安。這支【100% 無廣告 輕音樂合輯】，精心挑選高品質純音樂，以溫柔鋼琴、細膩旋律與療癒音頻為核心，只為陪伴你在讀書、學習、工作、冥想、放鬆、休息，甚至深度睡眠的每一刻。🎧...	https://www.youtube.com/watch?v=bVLRxsjM-jQ&list=RDbVLRxsjM-jQ&start_radio=1	https://i.ytimg.com/vi/bVLRxsjM-jQ/hqdefault.jpg	\N	{}	{"author": "Healing & Meditation", "publish_date": null, "video_id": "bVLRxsjM-jQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-10 20:38:06.129286	7	f	0	1	0
55	video	youtube	Deep Focus Music for Intense Work | Relaxing Study Beats & Concentration Flow	Achieve intense focus and sustained concentration with deep focus music designed for demanding work and relaxing study sessions. This soundscape helps calm t...	https://www.youtube.com/watch?v=Ri_REf-DLYA	https://i.ytimg.com/vi/Ri_REf-DLYA/hqdefault.jpg	\N	{}	{"author": "FocusRealm", "publish_date": null, "video_id": "Ri_REf-DLYA", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.67302	7	f	0	1	0
44	document	github	GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程	📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.	https://github.com/datawhalechina/hello-agents	https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents	\N	{}	{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-08 00:20:22.678277	5	f	0	1	0
60	document	github	GitHub - obra/superpowers: An agentic skills framework & software development methodology that works.	An agentic skills framework & software development methodology that works. - obra/superpowers	https://github.com/obra/superpowers	https://opengraph.githubassets.com/0d1e9ca8f944b149697f8ddfd9485d990cae8f0a20da9218b13af2926fadd6c7/obra/superpowers	\N	{}	{"author": "@github", "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.75009	7	f	0	2	0
57	video	youtube	YouTube Video hkGVpbVEScY	\N	https://www.youtube.com/watch?v=hkGVpbVEScY&list=RDhkGVpbVEScY&start_radio=1	https://i.ytimg.com/vi/hkGVpbVEScY/hqdefault.jpg	\N	{}	{"author": null, "publish_date": null, "video_id": "hkGVpbVEScY", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.714731	7	f	0	2	0
58	video	youtube	528 Hz - El Sonido Zen Tibetano Cura Todo El Cuerpo | Música para Paz Interior y Calmar Mente	528 Hz - El Sonido Zen Tibetano Cura Todo El Cuerpo | Música para Paz Interior y Calmar Mente___________________________________Bienvenido a mi canal, experi...	https://www.youtube.com/watch?v=e3T8ctg1D6I&list=RDe3T8ctg1D6I&start_radio=1	https://i.ytimg.com/vi/e3T8ctg1D6I/hqdefault.jpg	\N	{}	{"author": "Positive Energy for Soul", "publish_date": null, "video_id": "e3T8ctg1D6I", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.722346	7	f	0	2	0
56	video	youtube	4-HOUR STUDY WITH ME🌦️ / calm piano / A Rainy Day in Shinjuku, Tokyo / with countdown+alarm	🌦️ Here is the rainy night playlist:https://youtu.be/oDd6FjCXT_k👋 Hello everyone! Many of you loved the video featuring rain sounds in Shibuya🌧, so I’ve m...	https://www.youtube.com/watch?v=DXT9dF-WK-I	https://i.ytimg.com/vi/DXT9dF-WK-I/hqdefault.jpg	\N	{}	{"author": "Abao in Tokyo", "publish_date": null, "video_id": "DXT9dF-WK-I", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.706563	7	f	0	2	0
61	document	github	GitHub - h617265630/stepbystep	Contribute to h617265630/stepbystep development by creating an account on GitHub.	https://github.com/h617265630/stepbystep	https://opengraph.githubassets.com/92021c62239104a40166cfd0f99a9eb2d4a5a3ec3131da7d85ef6fec3f4fa77f/h617265630/stepbystep	\N	{}	{"author": "@github", "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}	2026-02-11 01:30:08.761154	7	f	0	1	0
59	video	x	Overtime: Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq	Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq	https://x.com/overtime/status/2020939399203258718?s=20	https://pbs.twimg.com/amplify_video_thumb/2020939344056352770/img/JzBxAJgSEKqnOU5m.jpg	\N	{}	{"author": "Overtime", "publish_date": "2026-02-09", "video_id": "2020939399203258718", "duration_seconds": null, "chapters": [], "og_type": "video.other", "og_video": "https://video.twimg.com/amplify_video/2020939344056352770/vid/avc1/720x1280/87QH_gaJglZgXvs1.mp4?tag=21", "twitter_player": null}	2026-02-11 01:30:08.740958	7	f	0	2	0
62	video	youtube	AI编程效率翻倍！Claude团队的10个内部技巧	Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.	https://www.youtube.com/watch?v=QIK5epmRwPI	https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg	\N	{}	{"author": "AI\\u968f\\u98ce", "publish_date": null, "video_id": "QIK5epmRwPI", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-11 03:55:55.160138	3	f	0	1	0
63	video	youtube	AI编程效率翻倍！Claude团队的10个内部技巧	Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.	https://www.youtube.com/watch?v=QIK5epmRwPI	https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg	\N	{}	{"author": "AI\\u968f\\u98ce", "publish_date": null, "video_id": "QIK5epmRwPI", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}	2026-02-12 15:07:45.051165	4	f	0	1	0
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id, granted_at) FROM stdin;
1	17	2026-01-10 17:30:29.582573
1	21	2026-01-10 17:30:29.582573
1	15	2026-01-10 17:30:29.582573
1	7	2026-01-10 17:30:29.582573
1	19	2026-01-10 17:30:29.582573
1	4	2026-01-10 17:30:29.582573
1	14	2026-01-10 17:30:29.582573
1	2	2026-01-10 17:30:29.582573
1	12	2026-01-10 17:30:29.582573
1	9	2026-01-10 17:30:29.582573
1	16	2026-01-10 17:30:29.582573
1	8	2026-01-10 17:30:29.582573
1	18	2026-01-10 17:30:29.582573
1	6	2026-01-10 17:30:29.582573
1	20	2026-01-10 17:30:29.582573
1	11	2026-01-10 17:30:29.582573
1	5	2026-01-10 17:30:29.582573
1	10	2026-01-10 17:30:29.582573
1	3	2026-01-10 17:30:29.582573
1	1	2026-01-10 17:30:29.582573
1	13	2026-01-10 17:30:29.582573
2	17	2026-01-10 17:30:29.587838
2	21	2026-01-10 17:30:29.587838
2	15	2026-01-10 17:30:29.587838
2	7	2026-01-10 17:30:29.587838
2	19	2026-01-10 17:30:29.587838
2	4	2026-01-10 17:30:29.587838
2	14	2026-01-10 17:30:29.587838
2	2	2026-01-10 17:30:29.587838
2	12	2026-01-10 17:30:29.587838
2	9	2026-01-10 17:30:29.587838
2	16	2026-01-10 17:30:29.587838
2	8	2026-01-10 17:30:29.587838
2	18	2026-01-10 17:30:29.587838
2	6	2026-01-10 17:30:29.587838
2	20	2026-01-10 17:30:29.587838
2	11	2026-01-10 17:30:29.587838
2	5	2026-01-10 17:30:29.587838
2	10	2026-01-10 17:30:29.587838
2	3	2026-01-10 17:30:29.587838
2	1	2026-01-10 17:30:29.587838
2	13	2026-01-10 17:30:29.587838
3	17	2026-01-10 17:30:29.591714
3	21	2026-01-10 17:30:29.591714
3	15	2026-01-10 17:30:29.591714
3	18	2026-01-10 17:30:29.591714
3	20	2026-01-10 17:30:29.591714
3	19	2026-01-10 17:30:29.591714
3	16	2026-01-10 17:30:29.591714
3	14	2026-01-10 17:30:29.591714
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, code, description, is_active, is_system, level, created_at, updated_at) FROM stdin;
1	超级管理员	super_admin	系统超级管理员，拥有所有权限	t	t	0	2026-01-10 17:30:29.579367	2026-01-10 17:30:29.579367
2	管理员	admin	系统管理员	t	t	10	2026-01-10 17:30:29.579367	2026-01-10 17:30:29.579367
3	编辑	editor	内容编辑	t	t	20	2026-01-10 17:30:29.579367	2026-01-10 17:30:29.579367
4	普通用户	user	普通用户	t	t	100	2026-01-10 17:30:29.579367	2026-01-10 17:30:29.579367
5	游客	guest	游客（未登录用户）	t	t	1000	2026-01-10 17:30:29.579367	2026-01-10 17:30:29.579367
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriptions (id, user_id, provider, provider_subscription_id, plan_code, status, current_period_start, current_period_end, cancel_at_period_end, created_at, updated_at) FROM stdin;
1	9	fastspring	dev_9	pro_monthly	active	2026-02-11 03:50:58.187006	2026-03-13 03:50:58.187006	f	2026-02-11 03:35:34.50578	2026-02-11 03:50:58.190019
\.


--
-- Data for Name: user_files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_files (id, user_id, title, file_type, original_filename, content_type, size_bytes, file_url, created_at, content) FROM stdin;
3	9	今天我干嘛	md	今天我干嘛.md	text/markdown	25	http://localhost:8000/static/user_files/file_9_1770730879.md	2026-02-10 21:41:19.493431	我的一些url 在这里
5	9	test	md	test.md	text/markdown	32	http://localhost:8000/static/user_files/file_9_1770733948.md	2026-02-10 22:32:28.891264	this is a test file ，我修改
4	9	one	md	one.md	text/markdown	442	http://localhost:8000/static/user_files/file_9_1770731023.md	2026-02-10 21:43:43.255749	https://www.youtube.com/watch?v=Ri_REf-DLYA  youtube ai\n\nhttps://www.youtube.com/watch?v=DXT9dF-WK-I  youtube 其他\n\nhttps://www.youtube.com/watch?v=hkGVpbVEScY&list=RDhkGVpbVEScY&start_radio=1 youtube 其他\n\nhttps://www.youtube.com/watch?v=e3T8ctg1D6I&list=RDe3T8ctg1D6I&start_radio=1 youtube 其他\n\nhttps://x.com/overtime/status/2020939399203258718?s=20 x ai\n\nhttps://github.com/obra/superpowers\n\nhttps://github.com/h617265630/stepbystep
6	9	3123	md	3123.md	text/markdown	3	http://localhost:8000/static/user_files/file_9_1770740493.md	2026-02-11 00:21:33.651632	123
\.


--
-- Data for Name: user_follows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_follows (follower_id, following_id, created_at) FROM stdin;
\.


--
-- Data for Name: user_images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_images (id, user_id, title, image_url, created_at) FROM stdin;
\.


--
-- Data for Name: user_learning_paths; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_learning_paths (user_id, learning_path_id) FROM stdin;
7	3
8	7
5	7
5	17
5	18
5	19
5	20
5	21
9	22
9	23
\.


--
-- Data for Name: user_resource; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_resource (user_id, resource_id, created_at, is_public, manual_weight, behavior_weight, effective_weight, added_at, last_opened, open_count, completion_status) FROM stdin;
9	52	2026-02-10 18:22:49.881478	t	1	\N	1	2026-02-10 18:22:49.877654	2026-02-10 19:19:37.591124	2	f
1	11	2026-01-26 06:40:43.871616	f	\N	\N	\N	\N	\N	0	f
1	12	2026-01-26 06:40:43.872837	f	\N	\N	\N	\N	\N	0	f
1	13	2026-01-26 06:40:43.87513	f	\N	\N	\N	\N	\N	0	f
1	14	2026-01-26 06:40:43.876591	f	\N	\N	\N	\N	\N	0	f
5	15	2026-01-26 06:43:24.586668	f	\N	\N	\N	\N	\N	0	f
5	16	2026-01-26 06:47:08.843674	t	\N	\N	\N	\N	\N	0	f
5	17	2026-01-26 06:48:19.558573	t	\N	\N	\N	\N	\N	0	f
5	19	2026-01-26 07:00:10.782236	t	\N	\N	\N	\N	\N	0	f
9	28	2026-02-10 20:34:31.04232	f	1	\N	1	2026-02-10 20:34:31.040145	\N	0	f
9	27	2026-02-10 20:34:41.243716	f	1	\N	1	2026-02-10 20:34:41.240186	\N	0	f
9	53	2026-02-10 20:29:54.473704	t	2	\N	2	2026-02-10 20:29:54.468478	2026-02-11 01:28:58.04202	3	f
5	26	2026-01-26 07:38:57.3595	t	\N	\N	\N	\N	\N	0	f
9	55	2026-02-11 01:30:08.687669	t	1	\N	1	2026-02-11 01:30:08.684826	\N	0	f
5	28	2026-01-31 02:51:04.50032	t	\N	\N	\N	\N	\N	0	f
5	29	2026-01-31 02:52:21.475121	t	\N	\N	\N	\N	\N	0	f
5	30	2026-02-01 06:25:07.749025	t	\N	\N	\N	\N	\N	0	f
5	31	2026-02-01 06:27:29.997965	t	\N	\N	\N	\N	\N	0	f
5	32	2026-02-01 06:42:11.754422	t	\N	\N	\N	\N	\N	0	f
5	33	2026-02-01 06:43:02.163838	t	\N	\N	\N	\N	\N	0	f
5	34	2026-02-01 06:43:57.74916	t	\N	\N	\N	\N	\N	0	f
9	35	2026-02-07 00:03:13.825849	t	\N	\N	\N	\N	\N	0	f
9	56	2026-02-11 01:30:08.709058	t	1	\N	1	2026-02-11 01:30:08.707876	\N	0	f
9	57	2026-02-11 01:30:08.716954	t	1	\N	1	2026-02-11 01:30:08.715983	\N	0	f
9	58	2026-02-11 01:30:08.72455	t	1	\N	1	2026-02-11 01:30:08.723794	\N	0	f
9	38	2026-02-07 02:26:58.679286	t	\N	\N	\N	\N	\N	0	f
9	39	2026-02-08 00:14:05.713069	t	\N	\N	\N	\N	\N	0	f
9	41	2026-02-08 00:19:36.686418	t	\N	\N	\N	\N	\N	0	f
9	43	2026-02-08 00:20:00.58896	t	\N	\N	\N	\N	\N	0	f
9	45	2026-02-08 00:24:04.317111	t	\N	\N	\N	\N	\N	0	f
9	59	2026-02-11 01:30:08.743578	t	1	\N	1	2026-02-11 01:30:08.742492	\N	0	f
9	60	2026-02-11 01:30:08.753701	t	1	\N	1	2026-02-11 01:30:08.752674	\N	0	f
9	61	2026-02-11 01:30:08.763574	t	1	\N	1	2026-02-11 01:30:08.762588	\N	0	f
10	59	2026-02-11 03:46:02.197353	f	1	\N	1	2026-02-11 03:46:02.194093	\N	0	f
10	58	2026-02-11 03:46:06.947727	f	1	\N	1	2026-02-11 03:46:06.945774	\N	0	f
10	57	2026-02-11 03:46:15.88491	f	1	\N	1	2026-02-11 03:46:15.883265	\N	0	f
10	60	2026-02-11 03:52:39.880567	f	1	\N	1	2026-02-11 03:52:39.878859	\N	0	f
10	56	2026-02-11 03:52:51.099936	f	1	\N	1	2026-02-11 03:52:51.091906	\N	0	f
10	45	2026-02-11 03:53:42.741814	f	1	\N	1	2026-02-11 03:53:42.739824	\N	0	f
10	44	2026-02-11 03:53:37.852586	f	2	\N	2	2026-02-11 03:53:37.849761	2026-02-11 03:54:00.718898	1	f
10	62	2026-02-11 03:55:55.208467	t	5	\N	5	2026-02-11 03:55:55.207014	\N	0	f
9	63	2026-02-12 15:07:45.091161	t	5	\N	5	2026-02-12 15:07:45.080278	\N	0	f
9	40	2026-02-08 00:19:08.328161	t	\N	\N	\N	\N	2026-02-28 15:44:14.355915	1	f
9	42	2026-02-08 00:19:46.288609	t	4	\N	4	\N	2026-02-28 15:45:45.681153	2	f
9	54	2026-02-10 20:38:06.1392	t	3	\N	3	2026-02-10 20:38:06.1349	2026-03-07 16:01:40.292241	1	f
9	48	2026-02-08 05:23:59.110199	t	3	\N	3	2026-02-08 05:23:59.107649	2026-02-08 06:23:10.845184	4	f
9	44	2026-02-08 00:20:22.682206	t	5	\N	5	\N	2026-02-08 06:26:25.72406	17	f
9	46	2026-02-08 00:25:09.944612	t	\N	\N	\N	\N	2026-02-09 05:20:22.43121	2	f
9	50	2026-02-09 05:22:04.238064	t	1	\N	1	2026-02-09 05:22:04.235093	\N	0	f
9	47	2026-02-08 05:17:21.070173	t	3	\N	3	2026-02-08 05:17:21.064252	2026-02-09 21:29:28.523526	12	f
9	49	2026-02-08 05:52:28.73924	t	3	\N	3	2026-02-08 05:52:28.735045	2026-02-09 21:36:12.86289	3	f
9	51	2026-02-10 18:22:17.619182	t	1	\N	1	2026-02-10 18:22:17.614531	\N	0	f
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (user_id, role_id, assigned_at) FROM stdin;
1	1	2026-01-10 18:14:52.324305
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, hashed_password, display_name, avatar_url, bio, created_at, updated_at, is_active, is_superuser) FROM stdin;
1	admin	admin@example.com	$2b$12$dtRfJQcrSdN.VDa/A9.6met85ngVdwc7aGTuWP9zzHxWGLyVpAdJK	系统管理员	\N	\N	2026-01-10 18:14:52.318968	2026-01-10 18:14:52.318971	t	t
2	datouwawa	datouwawa@qq.com	$2b$12$5VVDcbuTbBZjBYHWxApAQestCL/V4uXu9K7QU4XOuYDDxZqGjIJd.	\N	\N	\N	2026-01-10 18:16:21.187197	2026-01-10 18:16:21.187199	t	f
3	xiaotoubaba	xiaotou@qq.com	$2b$12$e16hY8GDAV3tEYTGFzUdXeYcw4E5aDLMWlBF6BYa1/Sew9bEvlLeu	\N	\N	\N	2026-01-10 18:20:56.596522	2026-01-10 18:20:56.596524	t	f
4	cage	cage@qq.com	$2b$12$uyMZREX9cPsb7zlNVSNUf.mr/zm3.gTqX48Qy8cziBPv/7naYqFrS	\N	\N	\N	2026-01-11 18:12:00.363548	2026-01-11 18:12:00.363551	t	f
5	user02	user02@qq.com	$2b$12$prj4fAX776oem9lPox86Re.pOizWWpn.nj1BfZrkAuhtV7kfcqEBy	\N	\N	\N	2026-01-11 19:36:31.805903	2026-01-11 19:36:31.805904	t	f
6	user03	user03@qq.com	$2b$12$mTyLdz0W9XgTygTQv3YAgeYQX5z334sQw3HaaI1TBqozvSMVcccOe	\N	\N	\N	2026-01-16 17:49:08.337434	2026-01-16 17:49:08.337436	t	f
7	copilot_8yo4ug	copilot_8yo4ug@example.com	$2b$12$IoLuqdu1nRsxJCegWrnvauG5o7yHkzKZHfv0HHaaaXlnaiR/DfcSa	\N	\N	\N	2026-01-19 14:32:46.528067	2026-01-19 14:32:46.528069	t	f
8	user05	user05@qq.com	$2b$12$/2JCP7922q5wibT9Mw3ul.GKcQ49q2lhrDreo6hofLx8zzkJCXEx.	\N	\N	\N	2026-01-20 13:33:26.342847	2026-01-20 13:33:26.342849	t	f
9	user06	user06@qq.com	$2b$12$LsATLv8Xwt3JuwGYTVB9.OmabTt.jWjeHvpVQIdX9tw/xtGIOrgXO	CageFree	http://localhost:8000/static/avatars/u_9_1770403228.png		2026-02-06 16:32:04.553347	2026-02-07 02:40:28.029845	t	t
10	cagefreejie	cagefree.jie@gmail.com	$2b$12$FCoHUAK0vmSlafZUDiCOh.H2SiOZx96pPzxPX4GOlhfO.YGPf.ceS	HUANG JIE	http://localhost:8000/static/avatars/u_10_1770752628.png		2026-02-11 03:38:18.414255	2026-02-11 03:43:48.944348	t	f
\.


--
-- Data for Name: videos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.videos (resource_id, duration, channel, video_id) FROM stdin;
11	\N	\N	\N
16	\N	StillMind Music	HQiMFS9eTYk
17	\N	FM RELAXING WORLD	q18spKfNYaw
18	\N	\N	\N
19	\N	\N	\N
30	\N	Pe Score	TUH7dgFlp0k
31	\N	马克的技术工作坊	AT4b9kLtQCQ
35	\N	马克的技术工作坊	GE0pFiFJTKo
38	\N	明星情报局Celebrity Intelligence Agency	98EZwfObm-o
47	\N	\N	\N
48	\N	Focusphere	yNAFtADhzss
49	\N	Healing & Meditation	bVLRxsjM-jQ
51	\N	\N	\N
52	\N	\N	\N
53	\N	Overtime	2020939399203258718
54	\N	Healing & Meditation	bVLRxsjM-jQ
55	\N	FocusRealm	Ri_REf-DLYA
56	\N	Abao in Tokyo	DXT9dF-WK-I
57	\N	\N	hkGVpbVEScY
58	\N	Positive Energy for Soul	e3T8ctg1D6I
59	\N	Overtime	2020939399203258718
62	\N	AI随风	QIK5epmRwPI
63	\N	AI随风	QIK5epmRwPI
\.


--
-- Data for Name: webhook_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webhook_events (id, provider, event_id, event_type, payload_json, headers_json, received_at, processed, error) FROM stdin;
1	fastspring	\N	\N	{}	{"host": "localhost:8000", "connection": "keep-alive", "content-length": "0", "sec-ch-ua-platform": "\\"macOS\\"", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36", "accept": "application/json", "sec-ch-ua": "\\"Not(A:Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"144\\", \\"Google Chrome\\";v=\\"144\\"", "sec-ch-ua-mobile": "?0", "origin": "http://localhost:8000", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "http://localhost:8000/docs", "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "zh-CN,zh;q=0.9,en;q=0.8", "cookie": "g_state={\\"i_l\\":0,\\"i_ll\\":1770753955775,\\"i_e\\":{\\"enable_itp_optimization\\":0},\\"i_b\\":\\"aFHwK4FG4UIVoJivquO2reRET8T6KmVAGDVobSpGm5g\\"}"}	2026-02-11 04:09:28.966614	f	Unable to parse webhook payload
2	fastspring	\N	\N	{}	{"host": "localhost:8000", "connection": "keep-alive", "content-length": "0", "sec-ch-ua-platform": "\\"macOS\\"", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36", "accept": "application/json", "sec-ch-ua": "\\"Not(A:Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"144\\", \\"Google Chrome\\";v=\\"144\\"", "sec-ch-ua-mobile": "?0", "origin": "http://localhost:8000", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "http://localhost:8000/docs", "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "zh-CN,zh;q=0.9,en;q=0.8", "cookie": "g_state={\\"i_l\\":0,\\"i_ll\\":1770753955775,\\"i_e\\":{\\"enable_itp_optimization\\":0},\\"i_b\\":\\"aFHwK4FG4UIVoJivquO2reRET8T6KmVAGDVobSpGm5g\\"}"}	2026-02-11 04:10:29.845451	f	Unable to parse webhook payload
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 43, true);


--
-- Name: docs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.docs_id_seq', 1, false);


--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.learning_path_comments_id_seq', 1, false);


--
-- Name: learning_paths_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.learning_paths_id_seq', 23, true);


--
-- Name: path_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.path_items_id_seq', 19, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 21, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- Name: progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.progress_id_seq', 3, true);


--
-- Name: resources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resources_id_seq', 63, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 5, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 1, true);


--
-- Name: user_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_files_id_seq', 6, true);


--
-- Name: user_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_images_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 10, true);


--
-- Name: webhook_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.webhook_events_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (resource_id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: docs_legacy docs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.docs_legacy
    ADD CONSTRAINT docs_pkey PRIMARY KEY (id);


--
-- Name: docs docs_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.docs
    ADD CONSTRAINT docs_pkey1 PRIMARY KEY (resource_id);


--
-- Name: learning_path_comments learning_path_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_path_comments
    ADD CONSTRAINT learning_path_comments_pkey PRIMARY KEY (id);


--
-- Name: learning_paths learning_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_paths
    ADD CONSTRAINT learning_paths_pkey PRIMARY KEY (id);


--
-- Name: path_items path_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items
    ADD CONSTRAINT path_items_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: progress progress_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progress
    ADD CONSTRAINT progress_pkey PRIMARY KEY (id);


--
-- Name: resources resources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT resources_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: path_items uq_learning_path_order; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items
    ADD CONSTRAINT uq_learning_path_order UNIQUE (learning_path_id, order_index);


--
-- Name: path_items uq_learning_path_resource; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items
    ADD CONSTRAINT uq_learning_path_resource UNIQUE (learning_path_id, resource_id);


--
-- Name: subscriptions uq_subscription_user_provider; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT uq_subscription_user_provider UNIQUE (user_id, provider);


--
-- Name: user_resource uq_user_resource; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_resource
    ADD CONSTRAINT uq_user_resource PRIMARY KEY (user_id, resource_id);


--
-- Name: user_files user_files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_files
    ADD CONSTRAINT user_files_pkey PRIMARY KEY (id);


--
-- Name: user_follows user_follows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT user_follows_pkey PRIMARY KEY (follower_id, following_id);


--
-- Name: user_images user_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_images
    ADD CONSTRAINT user_images_pkey PRIMARY KEY (id);


--
-- Name: user_learning_paths user_learning_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_learning_paths
    ADD CONSTRAINT user_learning_paths_pkey PRIMARY KEY (user_id, learning_path_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_pkey PRIMARY KEY (resource_id);


--
-- Name: webhook_events webhook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_events_pkey PRIMARY KEY (id);


--
-- Name: ix_categories_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_categories_code ON public.categories USING btree (code);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_categories_name ON public.categories USING btree (name);


--
-- Name: ix_docs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_docs_id ON public.docs_legacy USING btree (id);


--
-- Name: ix_docs_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_docs_name ON public.docs_legacy USING btree (name);


--
-- Name: ix_learning_path_comments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_learning_path_comments_id ON public.learning_path_comments USING btree (id);


--
-- Name: ix_learning_path_comments_learning_path_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_learning_path_comments_learning_path_id ON public.learning_path_comments USING btree (learning_path_id);


--
-- Name: ix_learning_path_comments_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_learning_path_comments_user_id ON public.learning_path_comments USING btree (user_id);


--
-- Name: ix_learning_paths_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_learning_paths_category_id ON public.learning_paths USING btree (category_id);


--
-- Name: ix_learning_paths_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_learning_paths_id ON public.learning_paths USING btree (id);


--
-- Name: ix_path_items_learning_path_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_path_items_learning_path_id ON public.path_items USING btree (learning_path_id);


--
-- Name: ix_path_items_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_path_items_resource_id ON public.path_items USING btree (resource_id);


--
-- Name: ix_permissions_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_products_name ON public.products USING btree (name);


--
-- Name: ix_resources_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_category_id ON public.resources USING btree (category_id);


--
-- Name: ix_resources_platform; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_platform ON public.resources USING btree (platform);


--
-- Name: ix_resources_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_resource_type ON public.resources USING btree (resource_type);


--
-- Name: ix_roles_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_code ON public.roles USING btree (code);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_subscriptions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_id ON public.subscriptions USING btree (id);


--
-- Name: ix_subscriptions_provider_subscription_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_subscriptions_provider_subscription_id ON public.subscriptions USING btree (provider_subscription_id);


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: ix_user_files_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_files_id ON public.user_files USING btree (id);


--
-- Name: ix_user_files_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_files_user_id ON public.user_files USING btree (user_id);


--
-- Name: ix_user_images_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_images_id ON public.user_images USING btree (id);


--
-- Name: ix_user_images_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_images_user_id ON public.user_images USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_videos_video_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_videos_video_id ON public.videos USING btree (video_id);


--
-- Name: ix_webhook_events_event_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_webhook_events_event_id ON public.webhook_events USING btree (event_id);


--
-- Name: ix_webhook_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_webhook_events_event_type ON public.webhook_events USING btree (event_type);


--
-- Name: ix_webhook_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_webhook_events_id ON public.webhook_events USING btree (id);


--
-- Name: articles articles_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id) ON DELETE CASCADE;


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(id);


--
-- Name: docs docs_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.docs
    ADD CONSTRAINT docs_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id) ON DELETE CASCADE;


--
-- Name: categories fk_categories_owner_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT fk_categories_owner_user_id_users FOREIGN KEY (owner_user_id) REFERENCES public.users(id);


--
-- Name: learning_paths fk_learning_paths_category_id_categories; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_paths
    ADD CONSTRAINT fk_learning_paths_category_id_categories FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: resources fk_resources_category_id_categories; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT fk_resources_category_id_categories FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: learning_path_comments learning_path_comments_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_path_comments
    ADD CONSTRAINT learning_path_comments_learning_path_id_fkey FOREIGN KEY (learning_path_id) REFERENCES public.learning_paths(id);


--
-- Name: learning_path_comments learning_path_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.learning_path_comments
    ADD CONSTRAINT learning_path_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: path_items path_items_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items
    ADD CONSTRAINT path_items_learning_path_id_fkey FOREIGN KEY (learning_path_id) REFERENCES public.learning_paths(id) ON DELETE CASCADE;


--
-- Name: path_items path_items_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.path_items
    ADD CONSTRAINT path_items_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id) ON DELETE CASCADE;


--
-- Name: progress progress_path_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progress
    ADD CONSTRAINT progress_path_item_id_fkey FOREIGN KEY (path_item_id) REFERENCES public.path_items(id) ON DELETE CASCADE;


--
-- Name: progress progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progress
    ADD CONSTRAINT progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id);


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_files user_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_files
    ADD CONSTRAINT user_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_follows user_follows_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT user_follows_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public.users(id);


--
-- Name: user_follows user_follows_following_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT user_follows_following_id_fkey FOREIGN KEY (following_id) REFERENCES public.users(id);


--
-- Name: user_images user_images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_images
    ADD CONSTRAINT user_images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_learning_paths user_learning_paths_learning_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_learning_paths
    ADD CONSTRAINT user_learning_paths_learning_path_id_fkey FOREIGN KEY (learning_path_id) REFERENCES public.learning_paths(id);


--
-- Name: user_learning_paths user_learning_paths_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_learning_paths
    ADD CONSTRAINT user_learning_paths_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_resource user_resource_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_resource
    ADD CONSTRAINT user_resource_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id);


--
-- Name: user_resource user_resource_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_resource
    ADD CONSTRAINT user_resource_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: videos videos_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict CYPwxxR2fqg7UEeOgM8TWTky1N4827chEQ93UlKYLbyqdusBAYx1pFefpuotf2Y

