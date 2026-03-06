-- 初始化默认分类数据
-- 使用 ON CONFLICT DO NOTHING 避免重复插入

INSERT INTO categories (name, code, level, is_leaf, is_system, owner_user_id, description)
VALUES 
    ('AI', 'ai', 0, true, true, NULL, 'AI related resources'),
    ('Design', 'design', 0, true, true, NULL, 'Design related resources'),
    ('UI', 'ui', 0, true, true, NULL, 'UI design related resources'),
    ('Frontend', 'frontend', 0, true, true, NULL, 'Frontend development related resources'),
    ('Backend', 'backend', 0, true, true, NULL, 'Backend development related resources'),
    ('Handmade', 'handmade', 0, true, true, NULL, 'Handmade / craft related resources'),
    ('Other', 'other', 0, true, true, NULL, 'Other resources')
ON CONFLICT (code) DO NOTHING;

-- 查询结果验证
SELECT id, name, code, is_system, owner_user_id FROM categories ORDER BY id;
