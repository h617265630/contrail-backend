SET session_replication_role = replica;

--
-- PostgreSQL database dump
--

-- \restrict ddHqjDEQbAcMq3ndqQVjzvKcZ3mE6eRaBKtDtM7L3HcF5j7OyPcJjfUJ6y1IDEv

-- Dumped from database version 15.15
-- Dumped by pg_dump version 17.6

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

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."alembic_version" ("version_num") VALUES
	('20260208_0001');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."users" ("id", "username", "email", "hashed_password", "display_name", "avatar_url", "bio", "created_at", "updated_at", "is_active", "is_superuser") VALUES
	(1, 'admin', 'admin@example.com', '$2b$12$dtRfJQcrSdN.VDa/A9.6met85ngVdwc7aGTuWP9zzHxWGLyVpAdJK', '系统管理员', NULL, NULL, '2026-01-10 18:14:52.318968', '2026-01-10 18:14:52.318971', true, true),
	(2, 'datouwawa', 'datouwawa@qq.com', '$2b$12$5VVDcbuTbBZjBYHWxApAQestCL/V4uXu9K7QU4XOuYDDxZqGjIJd.', NULL, NULL, NULL, '2026-01-10 18:16:21.187197', '2026-01-10 18:16:21.187199', true, false),
	(3, 'xiaotoubaba', 'xiaotou@qq.com', '$2b$12$e16hY8GDAV3tEYTGFzUdXeYcw4E5aDLMWlBF6BYa1/Sew9bEvlLeu', NULL, NULL, NULL, '2026-01-10 18:20:56.596522', '2026-01-10 18:20:56.596524', true, false),
	(4, 'cage', 'cage@qq.com', '$2b$12$uyMZREX9cPsb7zlNVSNUf.mr/zm3.gTqX48Qy8cziBPv/7naYqFrS', NULL, NULL, NULL, '2026-01-11 18:12:00.363548', '2026-01-11 18:12:00.363551', true, false),
	(5, 'user02', 'user02@qq.com', '$2b$12$prj4fAX776oem9lPox86Re.pOizWWpn.nj1BfZrkAuhtV7kfcqEBy', NULL, NULL, NULL, '2026-01-11 19:36:31.805903', '2026-01-11 19:36:31.805904', true, false),
	(6, 'user03', 'user03@qq.com', '$2b$12$mTyLdz0W9XgTygTQv3YAgeYQX5z334sQw3HaaI1TBqozvSMVcccOe', NULL, NULL, NULL, '2026-01-16 17:49:08.337434', '2026-01-16 17:49:08.337436', true, false),
	(7, 'copilot_8yo4ug', 'copilot_8yo4ug@example.com', '$2b$12$IoLuqdu1nRsxJCegWrnvauG5o7yHkzKZHfv0HHaaaXlnaiR/DfcSa', NULL, NULL, NULL, '2026-01-19 14:32:46.528067', '2026-01-19 14:32:46.528069', true, false),
	(8, 'user05', 'user05@qq.com', '$2b$12$/2JCP7922q5wibT9Mw3ul.GKcQ49q2lhrDreo6hofLx8zzkJCXEx.', NULL, NULL, NULL, '2026-01-20 13:33:26.342847', '2026-01-20 13:33:26.342849', true, false),
	(9, 'user06', 'user06@qq.com', '$2b$12$LsATLv8Xwt3JuwGYTVB9.OmabTt.jWjeHvpVQIdX9tw/xtGIOrgXO', 'CageFree', 'http://localhost:8000/static/avatars/u_9_1770403228.png', '', '2026-02-06 16:32:04.553347', '2026-02-07 02:40:28.029845', true, true),
	(10, 'cagefreejie', 'cagefree.jie@gmail.com', '$2b$12$FCoHUAK0vmSlafZUDiCOh.H2SiOZx96pPzxPX4GOlhfO.YGPf.ceS', 'HUANG JIE', 'http://localhost:8000/static/avatars/u_10_1770752628.png', '', '2026-02-11 03:38:18.414255', '2026-02-11 03:43:48.944348', true, false);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."categories" ("id", "name", "code", "parent_id", "level", "description", "is_leaf", "created_at", "is_system", "owner_user_id") VALUES
	(1, 'AI', 'ai', NULL, 0, NULL, true, '2026-01-17 01:30:32.899845', true, NULL),
	(2, '设计', 'design', NULL, 0, NULL, true, '2026-01-17 01:30:32.899847', true, NULL),
	(3, 'UI', 'ui', NULL, 0, NULL, true, '2026-01-17 01:30:32.899847', true, NULL),
	(4, '前端', 'frontend', NULL, 0, NULL, true, '2026-01-17 01:30:32.899848', true, NULL),
	(5, '后端', 'backend', NULL, 0, NULL, true, '2026-01-17 01:30:32.899849', true, NULL),
	(6, '手工', 'handmade', NULL, 0, NULL, true, '2026-01-17 01:30:32.899849', true, NULL),
	(7, '其他', 'other', NULL, 0, NULL, true, '2026-01-17 01:30:32.89985', true, NULL),
	(15, '🚀 Business & Productivity', 'business_productivity', NULL, 0, '🚀 Business & Productivity category', false, '2026-02-24 19:16:25.955109', true, NULL),
	(16, 'Startups', 'startups', 15, 1, 'Startups category', true, '2026-02-24 19:16:25.963261', true, NULL),
	(17, 'Entrepreneurship', 'entrepreneurship', 15, 1, 'Entrepreneurship category', true, '2026-02-24 19:16:25.964321', true, NULL),
	(18, 'Marketing', 'marketing', 15, 1, 'Marketing category', true, '2026-02-24 19:16:25.964946', true, NULL),
	(19, 'Finance', 'finance', 15, 1, 'Finance category', true, '2026-02-24 19:16:25.966119', true, NULL),
	(20, 'Productivity', 'productivity', 15, 1, 'Productivity category', true, '2026-02-24 19:16:25.966847', true, NULL),
	(21, 'Remote Work', 'remote_work', 15, 1, 'Remote Work category', true, '2026-02-24 19:16:25.967632', true, NULL),
	(22, '🏠 Lifestyle', 'lifestyle', NULL, 0, '🏠 Lifestyle category', false, '2026-02-24 19:16:25.968366', true, NULL),
	(23, 'Home Decor', 'home_decor', 22, 1, 'Home Decor category', true, '2026-02-24 19:16:25.968962', true, NULL),
	(24, 'Organization', 'organization', 22, 1, 'Organization category', true, '2026-02-24 19:16:25.96942', true, NULL),
	(25, 'Minimalism', 'minimalism', 22, 1, 'Minimalism category', true, '2026-02-24 19:16:25.969845', true, NULL),
	(26, 'Travel', 'travel', 22, 1, 'Travel category', true, '2026-02-24 19:16:25.97027', true, NULL),
	(27, 'Wellness', 'wellness', 22, 1, 'Wellness category', true, '2026-02-24 19:16:25.970687', true, NULL),
	(28, 'Fitness', 'fitness', 22, 1, 'Fitness category', true, '2026-02-24 19:16:25.971084', true, NULL),
	(29, '🍳 Food & Cooking', 'food_cooking', NULL, 0, '🍳 Food & Cooking category', false, '2026-02-24 19:16:25.971492', true, NULL),
	(30, 'Recipes', 'recipes', 29, 1, 'Recipes category', true, '2026-02-24 19:16:25.971883', true, NULL),
	(31, 'Baking', 'baking', 29, 1, 'Baking category', true, '2026-02-24 19:16:25.97226', true, NULL),
	(32, 'Healthy eating', 'healthy_eating', 29, 1, 'Healthy eating category', true, '2026-02-24 19:16:25.972985', true, NULL),
	(33, 'Meal prep', 'meal_prep', 29, 1, 'Meal prep category', true, '2026-02-24 19:16:25.973565', true, NULL),
	(34, '🎮 Entertainment', 'entertainment', NULL, 0, '🎮 Entertainment category', false, '2026-02-24 19:16:25.974313', true, NULL),
	(35, 'Gaming', 'gaming', 34, 1, 'Gaming category', true, '2026-02-24 19:16:25.974891', true, NULL),
	(36, 'Movies', 'movies', 34, 1, 'Movies category', true, '2026-02-24 19:16:25.975589', true, NULL),
	(37, 'Anime', 'anime', 34, 1, 'Anime category', true, '2026-02-24 19:16:25.976605', true, NULL),
	(38, 'Music', 'music', 34, 1, 'Music category', true, '2026-02-24 19:16:25.97846', true, NULL),
	(39, 'Pop Culture', 'pop_culture', 34, 1, 'Pop Culture category', true, '2026-02-24 19:16:25.980796', true, NULL),
	(40, '🧠 Personal Development', 'personal_development', NULL, 0, '🧠 Personal Development category', false, '2026-02-24 19:16:25.982044', true, NULL),
	(41, 'Habits', 'habits', 40, 1, 'Habits category', true, '2026-02-24 19:16:25.982916', true, NULL),
	(42, 'Psychology', 'psychology', 40, 1, 'Psychology category', true, '2026-02-24 19:16:25.983622', true, NULL),
	(43, 'Motivation', 'motivation', 40, 1, 'Motivation category', true, '2026-02-24 19:16:25.984446', true, NULL);


--
-- Data for Name: resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."resources" ("id", "resource_type", "platform", "title", "summary", "source_url", "thumbnail", "difficulty", "tags", "raw_meta", "created_at", "category_id", "is_system_public", "community_score", "save_count", "trending_score") VALUES
	(11, 'video', 'xiaohongshu', '【测试】小红书视频资源', '这是一个来自小红书的测试视频资源', 'https://www.xiaohongshu.com/explore/65a1b2c3d4e5f6g7h8i9j0k1', 'https://sns-img-qc.xhscdn.com/test.jpg', NULL, '{}', '{}', '2026-01-26 06:40:43.871616', 1, false, 0, 0, 0),
	(12, 'article', 'medium', '【测试】Understanding Machine Learning Basics', 'A comprehensive guide to machine learning fundamentals', 'https://medium.com/@example/understanding-machine-learning-basics-123abc', 'https://miro.medium.com/max/test.jpg', NULL, '{}', '{}', '2026-01-26 06:40:43.872837', 1, false, 0, 0, 0),
	(13, 'document', 'github', '【测试】OpenAI GPT-3 Repository', 'Official repository for GPT-3 documentation and examples', 'https://github.com/openai/gpt-3', 'https://opengraph.githubassets.com/test.png', NULL, '{}', '{}', '2026-01-26 06:40:43.87513', 1, false, 0, 0, 0),
	(14, 'article', 'medium', '【测试】Deep Learning Explained', 'An in-depth explanation of deep learning concepts and applications', 'https://medium.com/@techwriter/deep-learning-explained-456def', 'https://miro.medium.com/max/test2.jpg', NULL, '{}', '{}', '2026-01-26 06:40:43.876591', 1, false, 0, 0, 0),
	(15, 'article', 'barackobama.medium.com', 'a-wake-up-call-for-every-american-ec0115195303', NULL, 'https://barackobama.medium.com/a-wake-up-call-for-every-american-ec0115195303', NULL, NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-01-26 06:43:24.576788', 6, false, 0, 0, 0),
	(16, 'video', 'youtube', 'Relaxing Work Music | Zen Workspace Nordic Chill for Deep Concentration', NULL, 'https://www.youtube.com/watch?v=HQiMFS9eTYk&list=RDHQiMFS9eTYk&start_radio=1', 'https://i.ytimg.com/vi/HQiMFS9eTYk/hqdefault.jpg', NULL, '{}', '{"author": "StillMind Music", "publish_date": null, "video_id": "HQiMFS9eTYk", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-01-26 06:47:08.835216', 1, false, 0, 0, 0),
	(17, 'video', 'youtube', '【PEACEFUL PIANO BGM】一聽就能讓你放鬆！90分鐘的沉浸式舒壓旋律，溫柔的琴聲會撫平你的煩躁，陪你度過輕鬆又平靜的時光。特別適合用來冥想、放鬆，還有學習和工作時當背景音樂', NULL, 'https://www.youtube.com/watch?v=q18spKfNYaw', 'https://i.ytimg.com/vi/q18spKfNYaw/hqdefault.jpg', NULL, '{}', '{"author": "FM RELAXING WORLD", "publish_date": null, "video_id": "q18spKfNYaw", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-01-26 06:48:19.55493', 5, false, 0, 0, 0),
	(18, 'video', 'bilibili', '【2026最全面ComfyUI教程】B站强推！建议所有想学ComfyUI的同学，死磕这条视频，花了一周时间整理的ComfyUI零基础入门教程！_哔哩哔哩_bilibili', '【2026最全面ComfyUI教程】B站强推！建议所有想学ComfyUI的同学，死磕这条视频，花了一周时间整理的ComfyUI零基础入门教程！共计11条视频，包括：【Comfyui教程】2026最新中文版comfyui终极整合包、【Comfyui教程】第1节 课程概览与ComfyUI的优势、【Comfyui教程】第2节 ComfyUI界面导览与最基础生图流程等，UP主更多精彩视频，请关注UP账号。', 'https://www.bilibili.com/video/BV1pNvsBfEad/?spm_id_from=333.1007.tianma.1-1-1.click', '//i2.hdslb.com/bfs/archive/6da151b1eebb5ac8ff6c9c343d916acd6bb829cb.jpg@100w_100h_1c.png', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "video", "og_video": null, "twitter_player": null}', '2026-01-26 06:58:51.567546', 7, false, 0, 0, 0),
	(19, 'video', 'xiaohongshu', '野兽先生生日拿出50万抽奖给订阅的粉丝 - 小红书', '#野兽先生 #全网猎形行动 #野兽先生最新 #超自然行动组 #喜剧打开生活的另一面 #kpl #红薯地偶遇Rihanna #红薯地造梦师 #野生vlogger成长计划 #人生的意义', 'https://www.xiaohongshu.com/explore/6975d66e000000002203af20?xsec_token=ABys3qRV_zjUoTdTbuENMJwtVCp4SZ2PLT4FWzoQzWRG4=&xsec_source=pc_feed', NULL, NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-01-26 07:00:10.772724', 7, false, 0, 0, 0),
	(26, 'document', 'github', 'GitHub - openai/gpt-3: GPT-3: Language Models are Few-Shot Learners', 'GPT-3: Language Models are Few-Shot Learners. Contribute to openai/gpt-3 development by creating an account on GitHub.', 'https://github.com/openai/gpt-3', 'https://opengraph.githubassets.com/5a3dde964e04ec495a6a46b857bd8b20f32030f43d18df41067b6c412c0171ad/openai/gpt-3', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-01-26 07:38:57.350378', 7, false, 0, 0, 0),
	(29, 'document', 'github', 'GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞', 'Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞  - GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞', 'https://github.com/openclaw/openclaw', 'https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-01-31 02:52:21.47365', 7, false, 0, 0, 0),
	(30, 'video', 'youtube', '這個角度拍到 Luka 的出手真的太扯了', NULL, 'https://youtube.com/shorts/TUH7dgFlp0k?si=ie2tpN_uWpPmJrta', 'https://i.ytimg.com/vi/TUH7dgFlp0k/hq2.jpg', NULL, '{}', '{"author": "Pe Score", "publish_date": null, "video_id": "TUH7dgFlp0k", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-01 06:25:07.733948', 7, false, 0, 0, 0),
	(31, 'video', 'youtube', 'Claude Code 从 0 到 1 全攻略 —— MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理/ 后台任务 / 权限 ......', NULL, 'https://www.youtube.com/watch?v=AT4b9kLtQCQ', 'https://i.ytimg.com/vi/AT4b9kLtQCQ/hqdefault.jpg', NULL, '{}', '{"author": "\u9a6c\u514b\u7684\u6280\u672f\u5de5\u4f5c\u574a", "publish_date": null, "video_id": "AT4b9kLtQCQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-01 06:27:29.996726', 7, false, 0, 0, 0),
	(32, 'article', 'docs.clawd.bot', 'Setup - OpenClaw', NULL, 'https://docs.clawd.bot/start/setup', 'https://clawdhub.mintlify.app/mintlify-assets/_next/image?url=%2F_mintlify%2Fapi%2Fog%3Fdivision%3DStart%2BHere%26title%3DSetup%26logoLight%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26logoDark%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26primaryColor%3D%2523FF5A36%26backgroundLight%3D%2523ffffff%26backgroundDark%3D%25230a0d0d&w=1200&q=100', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}', '2026-02-01 06:42:11.745299', 7, false, 0, 0, 0),
	(33, 'article', 'skillsmp.com', 'nextlevelbuilder-ui-ux-pro-max-skill-claude-skills-ui-ux-pro-max-skill-md', NULL, 'https://skillsmp.com/zh/skills/nextlevelbuilder-ui-ux-pro-max-skill-claude-skills-ui-ux-pro-max-skill-md', NULL, NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-01 06:43:02.160636', 7, false, 0, 0, 0),
	(47, 'video', 'chatgpt.com', 'ChatGPT - 原生家庭与突破', 'ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster.', 'https://chatgpt.com/share/6987ab9a-d6d4-800b-b068-39723021952a', 'https://cdn.openai.com/chatgpt/share-og.png', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-08 05:17:21.053052', 7, false, 0, 1, 0),
	(48, 'video', 'youtube', 'Deep Focus Coding Music: Chillstep for Coding, Work & Study', NULL, 'https://www.youtube.com/watch?v=yNAFtADhzss&list=RDyNAFtADhzss&start_radio=1', 'https://i.ytimg.com/vi/yNAFtADhzss/hqdefault.jpg', NULL, '{}', '{"author": "Focusphere", "publish_date": null, "video_id": "yNAFtADhzss", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-08 05:23:59.097342', 7, false, 0, 1, 0),
	(49, 'video', 'youtube', '【100% 無廣告 ,輕音樂】一播放就進入心流狀態的極度專注讀書音樂 - 學習/閱讀/工作/放鬆音樂', NULL, 'https://www.youtube.com/watch?v=bVLRxsjM-jQ&list=RDbVLRxsjM-jQ&start_radio=1', 'https://i.ytimg.com/vi/bVLRxsjM-jQ/hqdefault.jpg', NULL, '{}', '{"author": "Healing & Meditation", "publish_date": null, "video_id": "bVLRxsjM-jQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-08 05:52:28.721279', 7, false, 0, 1, 0),
	(50, 'article', 'ui.shadcn.com', 'New Project - shadcn/ui', 'Customize everything. Pick your component library, icons, base color, theme, fonts and create your own version of shadcn/ui.', 'https://ui.shadcn.com/create?item=vercel', 'https://ui.shadcn.com/og.jpg', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}', '2026-02-09 05:22:04.223548', 7, false, 0, 1, 0),
	(27, 'document', 'github', 'GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞', 'Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞  - GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞', 'https://github.com/moltbot/moltbot', 'https://opengraph.githubassets.com/bca4deae4eb50f3ca8ac4603fd665a13f98883fbb48af0791b33d6d11950c932/openclaw/openclaw', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-01-31 02:48:56.376963', 7, false, 0, 1, 0),
	(34, 'article', 'docs.openclaw.ai', 'OpenClaw - OpenClaw', NULL, 'https://docs.openclaw.ai/', 'https://clawdhub.mintlify.app/mintlify-assets/_next/image?url=%2F_mintlify%2Fapi%2Fog%3Fdivision%3DStart%2BHere%26title%3DOpenClaw%26logoLight%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26logoDark%3Dhttps%253A%252F%252Fmintcdn.com%252Fclawdhub%252F4rYvG-uuZrMK_URE%252Fassets%252Fpixel-lobster.svg%253Ffit%253Dmax%2526auto%253Dformat%2526n%253D4rYvG-uuZrMK_URE%2526q%253D85%2526s%253Dda2032e9eac3b5d9bfe7eb96ca6a8a26%26primaryColor%3D%2523FF5A36%26backgroundLight%3D%2523ffffff%26backgroundDark%3D%25230a0d0d&w=1200&q=100', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "website", "og_video": null, "twitter_player": null}', '2026-02-01 06:43:57.739971', 7, false, 0, 0, 0),
	(35, 'video', 'youtube', 'Agent 的概念、原理与构建模式 —— 从零打造一个简化版的 Claude Code', NULL, 'https://www.youtube.com/watch?v=GE0pFiFJTKo', 'https://i.ytimg.com/vi/GE0pFiFJTKo/hqdefault.jpg', NULL, '{}', '{"author": "\u9a6c\u514b\u7684\u6280\u672f\u5de5\u4f5c\u574a", "publish_date": null, "video_id": "GE0pFiFJTKo", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-07 00:03:13.801234', 1, false, 0, 0, 0),
	(38, 'video', 'youtube', '【香蜜回忆杀】萨顶顶在环球综艺秀里面一首《左手指月》惊艳全场，耳朵怀孕了', NULL, 'https://www.youtube.com/watch?v=98EZwfObm-o&list=RD98EZwfObm-o&start_radio=1', 'https://i.ytimg.com/vi/98EZwfObm-o/hqdefault.jpg', NULL, '{}', '{"author": "\u660e\u661f\u60c5\u62a5\u5c40Celebrity Intelligence Agency", "publish_date": null, "video_id": "98EZwfObm-o", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-07 02:26:58.655737', 7, false, 0, 0, 0),
	(39, 'document', 'github', 'GitHub - Vanessa219/vditor: ♏ 一款浏览器端的 Markdown 编辑器，支持所见即所得（富文本）、即时渲染（类似 Typora）和分屏预览模式。An In-browser Markdown editor, support WYSIWYG (Rich Text), Instant Rendering (Typora-like) and Split View modes.', '♏  一款浏览器端的 Markdown 编辑器，支持所见即所得（富文本）、即时渲染（类似 Typora）和分屏预览模式。An In-browser Markdown editor, support WYSIWYG (Rich Text),  Instant Rendering (Typora-like) and Split View modes. - Vanessa219/vditor', 'https://github.com/Vanessa219/vditor', 'https://opengraph.githubassets.com/9c26857d3b61e501e83907a3401d468d57f91ce4c25566bc3a6d097c71dbaa47/Vanessa219/vditor', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:14:05.687279', 7, false, 0, 0, 0),
	(40, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:19:08.319082', 1, false, 0, 0, 0),
	(41, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:19:36.68228', 1, false, 0, 0, 0),
	(42, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:19:46.28529', 7, false, 0, 0, 0),
	(43, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:20:00.585549', 1, false, 0, 0, 0),
	(46, 'document', 'github', 'GitHub - fengdu78/Coursera-ML-AndrewNg-Notes: 吴恩达老师的机器学习课程个人笔记', '吴恩达老师的机器学习课程个人笔记. Contribute to fengdu78/Coursera-ML-AndrewNg-Notes development by creating an account on GitHub.', 'https://github.com/fengdu78/Coursera-ML-AndrewNg-Notes', 'https://opengraph.githubassets.com/7709ceddf6e41c7229705b9084595f56c8df9903b7d6c627d740ea20f8f60290/fengdu78/Coursera-ML-AndrewNg-Notes', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:25:09.938532', 7, false, 0, 0, 0),
	(45, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:24:04.310906', 6, false, 0, 1, 0),
	(51, 'video', 'x.com', '2020914244330324177', NULL, 'https://x.com/EHuanglu/status/2020914244330324177?s=20', NULL, NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-10 18:22:17.595864', 7, false, 0, 1, 0),
	(52, 'video', 'x.com', '2020914244330324177', NULL, 'https://x.com/EHuanglu/status/2020914244330324177?s=20', NULL, NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-10 18:22:49.871084', 7, false, 0, 1, 0),
	(53, 'video', 'x', 'Overtime: Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq', 'Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq', 'https://x.com/overtime/status/2020939399203258718?s=20', 'https://pbs.twimg.com/amplify_video_thumb/2020939344056352770/img/JzBxAJgSEKqnOU5m.jpg', NULL, '{}', '{"author": "Overtime", "publish_date": "2026-02-09", "video_id": "2020939399203258718", "duration_seconds": null, "chapters": [], "og_type": "video.other", "og_video": "https://video.twimg.com/amplify_video/2020939344056352770/vid/avc1/720x1280/87QH_gaJglZgXvs1.mp4?tag=21", "twitter_player": null}', '2026-02-10 20:29:54.455913', 7, false, 0, 1, 0),
	(28, 'document', 'github', 'GitHub - nextlevelbuilder/ui-ux-pro-max-skill: An AI SKILL that provide design intelligence for building professional UI/UX multiple platforms', 'An AI SKILL that provide design intelligence for building professional UI/UX multiple platforms - nextlevelbuilder/ui-ux-pro-max-skill', 'https://github.com/nextlevelbuilder/ui-ux-pro-max-skill', 'https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-01-31 02:51:04.49539', 7, false, 0, 1, 0),
	(54, 'video', 'youtube', '【100% 無廣告 ,輕音樂】一播放就進入心流狀態的極度專注讀書音樂 - 學習/閱讀/工作/放鬆音樂', '在這個節奏越來越快、壓力無處不在的世界裡，我們都需要一段真正安靜、沒有打擾、沒有廣告的時光，讓心慢慢沉靜下來，重新找回專注、平衡與內在的平安。這支【100% 無廣告 輕音樂合輯】，精心挑選高品質純音樂，以溫柔鋼琴、細膩旋律與療癒音頻為核心，只為陪伴你在讀書、學習、工作、冥想、放鬆、休息，甚至深度睡眠的每一刻。🎧...', 'https://www.youtube.com/watch?v=bVLRxsjM-jQ&list=RDbVLRxsjM-jQ&start_radio=1', 'https://i.ytimg.com/vi/bVLRxsjM-jQ/hqdefault.jpg', NULL, '{}', '{"author": "Healing & Meditation", "publish_date": null, "video_id": "bVLRxsjM-jQ", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-10 20:38:06.129286', 7, false, 0, 1, 0),
	(55, 'video', 'youtube', 'Deep Focus Music for Intense Work | Relaxing Study Beats & Concentration Flow', 'Achieve intense focus and sustained concentration with deep focus music designed for demanding work and relaxing study sessions. This soundscape helps calm t...', 'https://www.youtube.com/watch?v=Ri_REf-DLYA', 'https://i.ytimg.com/vi/Ri_REf-DLYA/hqdefault.jpg', NULL, '{}', '{"author": "FocusRealm", "publish_date": null, "video_id": "Ri_REf-DLYA", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.67302', 7, false, 0, 1, 0),
	(44, 'document', 'github', 'GitHub - datawhalechina/hello-agents: 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程', '📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程. Contribute to datawhalechina/hello-agents development by creating an account on GitHub.', 'https://github.com/datawhalechina/hello-agents', 'https://opengraph.githubassets.com/416efb42d893c210b6ddb82f57b31282444a32b8aa5de8efb77ee7284379fa5e/datawhalechina/hello-agents', NULL, '{}', '{"author": null, "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-08 00:20:22.678277', 5, false, 0, 1, 0),
	(60, 'document', 'github', 'GitHub - obra/superpowers: An agentic skills framework & software development methodology that works.', 'An agentic skills framework & software development methodology that works. - obra/superpowers', 'https://github.com/obra/superpowers', 'https://opengraph.githubassets.com/0d1e9ca8f944b149697f8ddfd9485d990cae8f0a20da9218b13af2926fadd6c7/obra/superpowers', NULL, '{}', '{"author": "@github", "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.75009', 7, false, 0, 2, 0),
	(57, 'video', 'youtube', 'YouTube Video hkGVpbVEScY', NULL, 'https://www.youtube.com/watch?v=hkGVpbVEScY&list=RDhkGVpbVEScY&start_radio=1', 'https://i.ytimg.com/vi/hkGVpbVEScY/hqdefault.jpg', NULL, '{}', '{"author": null, "publish_date": null, "video_id": "hkGVpbVEScY", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.714731', 7, false, 0, 2, 0),
	(58, 'video', 'youtube', '528 Hz - El Sonido Zen Tibetano Cura Todo El Cuerpo | Música para Paz Interior y Calmar Mente', '528 Hz - El Sonido Zen Tibetano Cura Todo El Cuerpo | Música para Paz Interior y Calmar Mente___________________________________Bienvenido a mi canal, experi...', 'https://www.youtube.com/watch?v=e3T8ctg1D6I&list=RDe3T8ctg1D6I&start_radio=1', 'https://i.ytimg.com/vi/e3T8ctg1D6I/hqdefault.jpg', NULL, '{}', '{"author": "Positive Energy for Soul", "publish_date": null, "video_id": "e3T8ctg1D6I", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.722346', 7, false, 0, 2, 0),
	(56, 'video', 'youtube', '4-HOUR STUDY WITH ME🌦️ / calm piano / A Rainy Day in Shinjuku, Tokyo / with countdown+alarm', '🌦️ Here is the rainy night playlist:https://youtu.be/oDd6FjCXT_k👋 Hello everyone! Many of you loved the video featuring rain sounds in Shibuya🌧, so I’ve m...', 'https://www.youtube.com/watch?v=DXT9dF-WK-I', 'https://i.ytimg.com/vi/DXT9dF-WK-I/hqdefault.jpg', NULL, '{}', '{"author": "Abao in Tokyo", "publish_date": null, "video_id": "DXT9dF-WK-I", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.706563', 7, false, 0, 2, 0),
	(61, 'document', 'github', 'GitHub - h617265630/stepbystep', 'Contribute to h617265630/stepbystep development by creating an account on GitHub.', 'https://github.com/h617265630/stepbystep', 'https://opengraph.githubassets.com/92021c62239104a40166cfd0f99a9eb2d4a5a3ec3131da7d85ef6fec3f4fa77f/h617265630/stepbystep', NULL, '{}', '{"author": "@github", "publish_date": null, "video_id": null, "duration_seconds": null, "chapters": [], "og_type": "object", "og_video": null, "twitter_player": null}', '2026-02-11 01:30:08.761154', 7, false, 0, 1, 0),
	(59, 'video', 'x', 'Overtime: Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq', 'Bro just cooked LeBron I’m done 😭 (h/t global.gxm/TT) pic.twitter.com/B7ADhRNbDq', 'https://x.com/overtime/status/2020939399203258718?s=20', 'https://pbs.twimg.com/amplify_video_thumb/2020939344056352770/img/JzBxAJgSEKqnOU5m.jpg', NULL, '{}', '{"author": "Overtime", "publish_date": "2026-02-09", "video_id": "2020939399203258718", "duration_seconds": null, "chapters": [], "og_type": "video.other", "og_video": "https://video.twimg.com/amplify_video/2020939344056352770/vid/avc1/720x1280/87QH_gaJglZgXvs1.mp4?tag=21", "twitter_player": null}', '2026-02-11 01:30:08.740958', 7, false, 0, 2, 0),
	(62, 'video', 'youtube', 'AI编程效率翻倍！Claude团队的10个内部技巧', 'Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.', 'https://www.youtube.com/watch?v=QIK5epmRwPI', 'https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg', NULL, '{}', '{"author": "AI\u968f\u98ce", "publish_date": null, "video_id": "QIK5epmRwPI", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-11 03:55:55.160138', 3, false, 0, 1, 0),
	(63, 'video', 'youtube', 'AI编程效率翻倍！Claude团队的10个内部技巧', 'Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.', 'https://www.youtube.com/watch?v=QIK5epmRwPI', 'https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg', NULL, '{}', '{"author": "AI\u968f\u98ce", "publish_date": null, "video_id": "QIK5epmRwPI", "duration_seconds": null, "chapters": [], "og_type": null, "og_video": null, "twitter_player": null}', '2026-02-12 15:07:45.051165', 4, false, 0, 1, 0);


--
-- Data for Name: articles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."articles" ("resource_id", "publisher", "published_at") VALUES
	(12, NULL, NULL),
	(14, NULL, NULL),
	(15, NULL, NULL),
	(32, NULL, NULL),
	(33, NULL, NULL),
	(34, NULL, NULL),
	(50, NULL, NULL);


--
-- Data for Name: docs; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."docs" ("resource_id", "doc_type", "version") VALUES
	(13, NULL, NULL),
	(26, NULL, NULL),
	(27, NULL, NULL),
	(28, NULL, NULL),
	(29, NULL, NULL),
	(39, NULL, NULL),
	(40, NULL, NULL),
	(41, NULL, NULL),
	(42, NULL, NULL),
	(43, NULL, NULL),
	(44, NULL, NULL),
	(45, NULL, NULL),
	(46, NULL, NULL),
	(60, NULL, NULL),
	(61, NULL, NULL);


--
-- Data for Name: docs_legacy; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: learning_paths; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."learning_paths" ("id", "title", "description", "is_public", "is_active", "category_id", "cover_image_url", "type") VALUES
	(7, 'flutter应用', '一个flutter', true, true, 2, 'https://i.ytimg.com/vi/VyR8nqD3sQ8/hqdefault.jpg', NULL),
	(3, 'My Path 8yo4ug', 'desc', false, true, 7, NULL, NULL),
	(17, 'github 相关项目', '123', true, true, 2, 'https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432', NULL),
	(18, 'linear path', '123', true, true, 3, 'https://repository-images.githubusercontent.com/1106996539/d7c84c2d-e797-405f-a868-87fb194e8432', 'linear path'),
	(19, 'stuctured path', '123', true, true, 5, 'https://opengraph.githubassets.com/5a3dde964e04ec495a6a46b857bd8b20f32030f43d18df41067b6c412c0171ad/openai/gpt-3', 'partical pool'),
	(20, 'partical pool', 'partical''', true, true, 3, 'https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw', 'partical pool'),
	(21, 'stucted', '123', true, true, 7, 'https://opengraph.githubassets.com/c0be26a6d16daf319ff06e98696a3b6dfe8fc5f79c87b47b2643fc5ce35f54d3/openclaw/openclaw', 'structured path'),
	(22, 'GitHub Trends Weekly', 'Track GitHub Trending weekly: shortlist repos, read READMEs, capture key ideas, and turn them into an actionable learning path.', true, true, 7, 'https://i.ytimg.com/vi/98EZwfObm-o/hqdefault.jpg', 'linear path'),
	(23, 'GitHub Trends Weekly', 'Track GitHub Trending weekly: shortlist repos, read READMEs, capture key ideas, and turn them into an actionable learning path.', true, true, 5, 'https://i.ytimg.com/vi/QIK5epmRwPI/hqdefault.jpg', 'linear path');


--
-- Data for Name: learning_path_comments; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: path_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."path_items" ("id", "learning_path_id", "resource_id", "order_index", "stage", "purpose", "estimated_time", "is_optional") VALUES
	(2, 7, 17, 1, NULL, NULL, NULL, false),
	(3, 7, 16, 2, NULL, NULL, NULL, false),
	(4, 7, 15, 3, NULL, NULL, NULL, false),
	(5, 7, 14, 4, NULL, NULL, NULL, false),
	(6, 7, 13, 5, NULL, NULL, NULL, false),
	(10, 17, 28, 1, NULL, NULL, NULL, false),
	(11, 18, 28, 1, NULL, NULL, NULL, false),
	(12, 19, 26, 1, NULL, NULL, NULL, false),
	(13, 20, 29, 1, NULL, NULL, NULL, false),
	(14, 21, 29, 1, NULL, NULL, NULL, false),
	(15, 22, 38, 1, NULL, NULL, NULL, false),
	(16, 22, 39, 2, NULL, NULL, NULL, false),
	(17, 23, 59, 1, NULL, NULL, NULL, false),
	(18, 23, 58, 2, NULL, NULL, NULL, false),
	(19, 23, 60, 3, NULL, NULL, NULL, false);


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."permissions" ("id", "name", "code", "description", "module", "action", "is_active", "created_at", "updated_at") VALUES
	(1, '查看用户', 'user.read', NULL, 'user', 'read', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(2, '创建用户', 'user.create', NULL, 'user', 'create', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(3, '更新用户', 'user.update', NULL, 'user', 'update', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(4, '删除用户', 'user.delete', NULL, 'user', 'delete', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(5, '管理用户角色', 'user.role.manage', NULL, 'user', 'role_manage', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(6, '查看角色', 'role.read', NULL, 'role', 'read', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(7, '创建角色', 'role.create', NULL, 'role', 'create', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(8, '更新角色', 'role.update', NULL, 'role', 'update', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(9, '删除角色', 'role.delete', NULL, 'role', 'delete', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(10, '查看权限', 'permission.read', NULL, 'permission', 'read', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(11, '创建权限', 'permission.create', NULL, 'permission', 'create', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(12, '更新权限', 'permission.update', NULL, 'permission', 'update', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(13, '删除权限', 'permission.delete', NULL, 'permission', 'delete', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(14, '查看视频', 'video.read', NULL, 'video', 'read', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(15, '上传视频', 'video.upload', NULL, 'video', 'upload', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(16, '编辑视频', 'video.update', NULL, 'video', 'update', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(17, '删除视频', 'video.delete', NULL, 'video', 'delete', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(18, '查看剪辑', 'clip.read', NULL, 'clip', 'read', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(19, '创建剪辑', 'clip.create', NULL, 'clip', 'create', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(20, '编辑剪辑', 'clip.update', NULL, 'clip', 'update', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029'),
	(21, '删除剪辑', 'clip.delete', NULL, 'clip', 'delete', true, '2026-01-10 17:30:29.570029', '2026-01-10 17:30:29.570029');


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."progress" ("id", "user_id", "path_item_id", "last_watched_time", "progress_percentage") VALUES
	(3, 9, 19, '2026-02-12 07:24:43.428048', 95);


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."roles" ("id", "name", "code", "description", "is_active", "is_system", "level", "created_at", "updated_at") VALUES
	(1, '超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', true, true, 0, '2026-01-10 17:30:29.579367', '2026-01-10 17:30:29.579367'),
	(2, '管理员', 'admin', '系统管理员', true, true, 10, '2026-01-10 17:30:29.579367', '2026-01-10 17:30:29.579367'),
	(3, '编辑', 'editor', '内容编辑', true, true, 20, '2026-01-10 17:30:29.579367', '2026-01-10 17:30:29.579367'),
	(4, '普通用户', 'user', '普通用户', true, true, 100, '2026-01-10 17:30:29.579367', '2026-01-10 17:30:29.579367'),
	(5, '游客', 'guest', '游客（未登录用户）', true, true, 1000, '2026-01-10 17:30:29.579367', '2026-01-10 17:30:29.579367');


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."role_permissions" ("role_id", "permission_id", "granted_at") VALUES
	(1, 17, '2026-01-10 17:30:29.582573'),
	(1, 21, '2026-01-10 17:30:29.582573'),
	(1, 15, '2026-01-10 17:30:29.582573'),
	(1, 7, '2026-01-10 17:30:29.582573'),
	(1, 19, '2026-01-10 17:30:29.582573'),
	(1, 4, '2026-01-10 17:30:29.582573'),
	(1, 14, '2026-01-10 17:30:29.582573'),
	(1, 2, '2026-01-10 17:30:29.582573'),
	(1, 12, '2026-01-10 17:30:29.582573'),
	(1, 9, '2026-01-10 17:30:29.582573'),
	(1, 16, '2026-01-10 17:30:29.582573'),
	(1, 8, '2026-01-10 17:30:29.582573'),
	(1, 18, '2026-01-10 17:30:29.582573'),
	(1, 6, '2026-01-10 17:30:29.582573'),
	(1, 20, '2026-01-10 17:30:29.582573'),
	(1, 11, '2026-01-10 17:30:29.582573'),
	(1, 5, '2026-01-10 17:30:29.582573'),
	(1, 10, '2026-01-10 17:30:29.582573'),
	(1, 3, '2026-01-10 17:30:29.582573'),
	(1, 1, '2026-01-10 17:30:29.582573'),
	(1, 13, '2026-01-10 17:30:29.582573'),
	(2, 17, '2026-01-10 17:30:29.587838'),
	(2, 21, '2026-01-10 17:30:29.587838'),
	(2, 15, '2026-01-10 17:30:29.587838'),
	(2, 7, '2026-01-10 17:30:29.587838'),
	(2, 19, '2026-01-10 17:30:29.587838'),
	(2, 4, '2026-01-10 17:30:29.587838'),
	(2, 14, '2026-01-10 17:30:29.587838'),
	(2, 2, '2026-01-10 17:30:29.587838'),
	(2, 12, '2026-01-10 17:30:29.587838'),
	(2, 9, '2026-01-10 17:30:29.587838'),
	(2, 16, '2026-01-10 17:30:29.587838'),
	(2, 8, '2026-01-10 17:30:29.587838'),
	(2, 18, '2026-01-10 17:30:29.587838'),
	(2, 6, '2026-01-10 17:30:29.587838'),
	(2, 20, '2026-01-10 17:30:29.587838'),
	(2, 11, '2026-01-10 17:30:29.587838'),
	(2, 5, '2026-01-10 17:30:29.587838'),
	(2, 10, '2026-01-10 17:30:29.587838'),
	(2, 3, '2026-01-10 17:30:29.587838'),
	(2, 1, '2026-01-10 17:30:29.587838'),
	(2, 13, '2026-01-10 17:30:29.587838'),
	(3, 17, '2026-01-10 17:30:29.591714'),
	(3, 21, '2026-01-10 17:30:29.591714'),
	(3, 15, '2026-01-10 17:30:29.591714'),
	(3, 18, '2026-01-10 17:30:29.591714'),
	(3, 20, '2026-01-10 17:30:29.591714'),
	(3, 19, '2026-01-10 17:30:29.591714'),
	(3, 16, '2026-01-10 17:30:29.591714'),
	(3, 14, '2026-01-10 17:30:29.591714');


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."subscriptions" ("id", "user_id", "provider", "provider_subscription_id", "plan_code", "status", "current_period_start", "current_period_end", "cancel_at_period_end", "created_at", "updated_at") VALUES
	(1, 9, 'fastspring', 'dev_9', 'pro_monthly', 'active', '2026-02-11 03:50:58.187006', '2026-03-13 03:50:58.187006', false, '2026-02-11 03:35:34.50578', '2026-02-11 03:50:58.190019');


--
-- Data for Name: user_files; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."user_files" ("id", "user_id", "title", "file_type", "original_filename", "content_type", "size_bytes", "file_url", "created_at", "content") VALUES
	(3, 9, '今天我干嘛', 'md', '今天我干嘛.md', 'text/markdown', 25, 'http://localhost:8000/static/user_files/file_9_1770730879.md', '2026-02-10 21:41:19.493431', '我的一些url 在这里'),
	(5, 9, 'test', 'md', 'test.md', 'text/markdown', 32, 'http://localhost:8000/static/user_files/file_9_1770733948.md', '2026-02-10 22:32:28.891264', 'this is a test file ，我修改'),
	(4, 9, 'one', 'md', 'one.md', 'text/markdown', 442, 'http://localhost:8000/static/user_files/file_9_1770731023.md', '2026-02-10 21:43:43.255749', 'https://www.youtube.com/watch?v=Ri_REf-DLYA  youtube ai

https://www.youtube.com/watch?v=DXT9dF-WK-I  youtube 其他

https://www.youtube.com/watch?v=hkGVpbVEScY&list=RDhkGVpbVEScY&start_radio=1 youtube 其他

https://www.youtube.com/watch?v=e3T8ctg1D6I&list=RDe3T8ctg1D6I&start_radio=1 youtube 其他

https://x.com/overtime/status/2020939399203258718?s=20 x ai

https://github.com/obra/superpowers

https://github.com/h617265630/stepbystep'),
	(6, 9, '3123', 'md', '3123.md', 'text/markdown', 3, 'http://localhost:8000/static/user_files/file_9_1770740493.md', '2026-02-11 00:21:33.651632', '123');


--
-- Data for Name: user_follows; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: user_images; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: user_learning_paths; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."user_learning_paths" ("user_id", "learning_path_id") VALUES
	(7, 3),
	(8, 7),
	(5, 7),
	(5, 17),
	(5, 18),
	(5, 19),
	(5, 20),
	(5, 21),
	(9, 22),
	(9, 23);


--
-- Data for Name: user_resource; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."user_resource" ("user_id", "resource_id", "created_at", "is_public", "manual_weight", "behavior_weight", "effective_weight", "added_at", "last_opened", "open_count", "completion_status") VALUES
	(9, 52, '2026-02-10 18:22:49.881478', true, 1, NULL, 1, '2026-02-10 18:22:49.877654', '2026-02-10 19:19:37.591124', 2, false),
	(1, 11, '2026-01-26 06:40:43.871616', false, NULL, NULL, NULL, NULL, NULL, 0, false),
	(1, 12, '2026-01-26 06:40:43.872837', false, NULL, NULL, NULL, NULL, NULL, 0, false),
	(1, 13, '2026-01-26 06:40:43.87513', false, NULL, NULL, NULL, NULL, NULL, 0, false),
	(1, 14, '2026-01-26 06:40:43.876591', false, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 15, '2026-01-26 06:43:24.586668', false, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 16, '2026-01-26 06:47:08.843674', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 17, '2026-01-26 06:48:19.558573', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 19, '2026-01-26 07:00:10.782236', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 28, '2026-02-10 20:34:31.04232', false, 1, NULL, 1, '2026-02-10 20:34:31.040145', NULL, 0, false),
	(9, 27, '2026-02-10 20:34:41.243716', false, 1, NULL, 1, '2026-02-10 20:34:41.240186', NULL, 0, false),
	(9, 53, '2026-02-10 20:29:54.473704', true, 2, NULL, 2, '2026-02-10 20:29:54.468478', '2026-02-11 01:28:58.04202', 3, false),
	(5, 26, '2026-01-26 07:38:57.3595', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 55, '2026-02-11 01:30:08.687669', true, 1, NULL, 1, '2026-02-11 01:30:08.684826', NULL, 0, false),
	(5, 28, '2026-01-31 02:51:04.50032', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 29, '2026-01-31 02:52:21.475121', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 30, '2026-02-01 06:25:07.749025', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 31, '2026-02-01 06:27:29.997965', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 32, '2026-02-01 06:42:11.754422', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 33, '2026-02-01 06:43:02.163838', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(5, 34, '2026-02-01 06:43:57.74916', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 35, '2026-02-07 00:03:13.825849', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 56, '2026-02-11 01:30:08.709058', true, 1, NULL, 1, '2026-02-11 01:30:08.707876', NULL, 0, false),
	(9, 57, '2026-02-11 01:30:08.716954', true, 1, NULL, 1, '2026-02-11 01:30:08.715983', NULL, 0, false),
	(9, 58, '2026-02-11 01:30:08.72455', true, 1, NULL, 1, '2026-02-11 01:30:08.723794', NULL, 0, false),
	(9, 38, '2026-02-07 02:26:58.679286', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 39, '2026-02-08 00:14:05.713069', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 41, '2026-02-08 00:19:36.686418', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 43, '2026-02-08 00:20:00.58896', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 45, '2026-02-08 00:24:04.317111', true, NULL, NULL, NULL, NULL, NULL, 0, false),
	(9, 59, '2026-02-11 01:30:08.743578', true, 1, NULL, 1, '2026-02-11 01:30:08.742492', NULL, 0, false),
	(9, 60, '2026-02-11 01:30:08.753701', true, 1, NULL, 1, '2026-02-11 01:30:08.752674', NULL, 0, false),
	(9, 61, '2026-02-11 01:30:08.763574', true, 1, NULL, 1, '2026-02-11 01:30:08.762588', NULL, 0, false),
	(10, 59, '2026-02-11 03:46:02.197353', false, 1, NULL, 1, '2026-02-11 03:46:02.194093', NULL, 0, false),
	(10, 58, '2026-02-11 03:46:06.947727', false, 1, NULL, 1, '2026-02-11 03:46:06.945774', NULL, 0, false),
	(10, 57, '2026-02-11 03:46:15.88491', false, 1, NULL, 1, '2026-02-11 03:46:15.883265', NULL, 0, false),
	(10, 60, '2026-02-11 03:52:39.880567', false, 1, NULL, 1, '2026-02-11 03:52:39.878859', NULL, 0, false),
	(10, 56, '2026-02-11 03:52:51.099936', false, 1, NULL, 1, '2026-02-11 03:52:51.091906', NULL, 0, false),
	(10, 45, '2026-02-11 03:53:42.741814', false, 1, NULL, 1, '2026-02-11 03:53:42.739824', NULL, 0, false),
	(10, 44, '2026-02-11 03:53:37.852586', false, 2, NULL, 2, '2026-02-11 03:53:37.849761', '2026-02-11 03:54:00.718898', 1, false),
	(10, 62, '2026-02-11 03:55:55.208467', true, 5, NULL, 5, '2026-02-11 03:55:55.207014', NULL, 0, false),
	(9, 63, '2026-02-12 15:07:45.091161', true, 5, NULL, 5, '2026-02-12 15:07:45.080278', NULL, 0, false),
	(9, 40, '2026-02-08 00:19:08.328161', true, NULL, NULL, NULL, NULL, '2026-02-28 15:44:14.355915', 1, false),
	(9, 42, '2026-02-08 00:19:46.288609', true, 4, NULL, 4, NULL, '2026-02-28 15:45:45.681153', 2, false),
	(9, 54, '2026-02-10 20:38:06.1392', true, 3, NULL, 3, '2026-02-10 20:38:06.1349', '2026-03-07 16:01:40.292241', 1, false),
	(9, 48, '2026-02-08 05:23:59.110199', true, 3, NULL, 3, '2026-02-08 05:23:59.107649', '2026-02-08 06:23:10.845184', 4, false),
	(9, 44, '2026-02-08 00:20:22.682206', true, 5, NULL, 5, NULL, '2026-02-08 06:26:25.72406', 17, false),
	(9, 46, '2026-02-08 00:25:09.944612', true, NULL, NULL, NULL, NULL, '2026-02-09 05:20:22.43121', 2, false),
	(9, 50, '2026-02-09 05:22:04.238064', true, 1, NULL, 1, '2026-02-09 05:22:04.235093', NULL, 0, false),
	(9, 47, '2026-02-08 05:17:21.070173', true, 3, NULL, 3, '2026-02-08 05:17:21.064252', '2026-02-09 21:29:28.523526', 12, false),
	(9, 49, '2026-02-08 05:52:28.73924', true, 3, NULL, 3, '2026-02-08 05:52:28.735045', '2026-02-09 21:36:12.86289', 3, false),
	(9, 51, '2026-02-10 18:22:17.619182', true, 1, NULL, 1, '2026-02-10 18:22:17.614531', NULL, 0, false);


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."user_roles" ("user_id", "role_id", "assigned_at") VALUES
	(1, 1, '2026-01-10 18:14:52.324305');


--
-- Data for Name: videos; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."videos" ("resource_id", "duration", "channel", "video_id") VALUES
	(11, NULL, NULL, NULL),
	(16, NULL, 'StillMind Music', 'HQiMFS9eTYk'),
	(17, NULL, 'FM RELAXING WORLD', 'q18spKfNYaw'),
	(18, NULL, NULL, NULL),
	(19, NULL, NULL, NULL),
	(30, NULL, 'Pe Score', 'TUH7dgFlp0k'),
	(31, NULL, '马克的技术工作坊', 'AT4b9kLtQCQ'),
	(35, NULL, '马克的技术工作坊', 'GE0pFiFJTKo'),
	(38, NULL, '明星情报局Celebrity Intelligence Agency', '98EZwfObm-o'),
	(47, NULL, NULL, NULL),
	(48, NULL, 'Focusphere', 'yNAFtADhzss'),
	(49, NULL, 'Healing & Meditation', 'bVLRxsjM-jQ'),
	(51, NULL, NULL, NULL),
	(52, NULL, NULL, NULL),
	(53, NULL, 'Overtime', '2020939399203258718'),
	(54, NULL, 'Healing & Meditation', 'bVLRxsjM-jQ'),
	(55, NULL, 'FocusRealm', 'Ri_REf-DLYA'),
	(56, NULL, 'Abao in Tokyo', 'DXT9dF-WK-I'),
	(57, NULL, NULL, 'hkGVpbVEScY'),
	(58, NULL, 'Positive Energy for Soul', 'e3T8ctg1D6I'),
	(59, NULL, 'Overtime', '2020939399203258718'),
	(62, NULL, 'AI随风', 'QIK5epmRwPI'),
	(63, NULL, 'AI随风', 'QIK5epmRwPI');


--
-- Data for Name: webhook_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."webhook_events" ("id", "provider", "event_id", "event_type", "payload_json", "headers_json", "received_at", "processed", "error") VALUES
	(1, 'fastspring', NULL, NULL, '{}', '{"host": "localhost:8000", "connection": "keep-alive", "content-length": "0", "sec-ch-ua-platform": "\"macOS\"", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36", "accept": "application/json", "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"", "sec-ch-ua-mobile": "?0", "origin": "http://localhost:8000", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "http://localhost:8000/docs", "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "zh-CN,zh;q=0.9,en;q=0.8", "cookie": "g_state={\"i_l\":0,\"i_ll\":1770753955775,\"i_e\":{\"enable_itp_optimization\":0},\"i_b\":\"aFHwK4FG4UIVoJivquO2reRET8T6KmVAGDVobSpGm5g\"}"}', '2026-02-11 04:09:28.966614', false, 'Unable to parse webhook payload'),
	(2, 'fastspring', NULL, NULL, '{}', '{"host": "localhost:8000", "connection": "keep-alive", "content-length": "0", "sec-ch-ua-platform": "\"macOS\"", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36", "accept": "application/json", "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"", "sec-ch-ua-mobile": "?0", "origin": "http://localhost:8000", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "http://localhost:8000/docs", "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "zh-CN,zh;q=0.9,en;q=0.8", "cookie": "g_state={\"i_l\":0,\"i_ll\":1770753955775,\"i_e\":{\"enable_itp_optimization\":0},\"i_b\":\"aFHwK4FG4UIVoJivquO2reRET8T6KmVAGDVobSpGm5g\"}"}', '2026-02-11 04:10:29.845451', false, 'Unable to parse webhook payload');


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."categories_id_seq"', 43, true);


--
-- Name: docs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."docs_id_seq"', 1, false);


--
-- Name: learning_path_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."learning_path_comments_id_seq"', 1, false);


--
-- Name: learning_paths_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."learning_paths_id_seq"', 23, true);


--
-- Name: path_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."path_items_id_seq"', 19, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."permissions_id_seq"', 21, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."products_id_seq"', 1, false);


--
-- Name: progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."progress_id_seq"', 3, true);


--
-- Name: resources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."resources_id_seq"', 63, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."roles_id_seq"', 5, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."subscriptions_id_seq"', 1, true);


--
-- Name: user_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."user_files_id_seq"', 6, true);


--
-- Name: user_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."user_images_id_seq"', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."users_id_seq"', 10, true);


--
-- Name: webhook_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."webhook_events_id_seq"', 2, true);


--
-- PostgreSQL database dump complete
--

-- \unrestrict ddHqjDEQbAcMq3ndqQVjzvKcZ3mE6eRaBKtDtM7L3HcF5j7OyPcJjfUJ6y1IDEv

RESET ALL;
