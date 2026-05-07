"""Login.vue 系统修复脚本"""
import re

p = '\ufffd?'  # 损坏模式

with open(r'E:\event-intelligent\frontend\src\views\Login.vue', encoding='utf-8', errors='replace') as f:
    c = f.read()

before_count = c.count(p)

# ===== 1. HTML 模板修复 =====
# 顶部标题注释
c = c.replace('<!-- ===== 顶部标题' + p + '===== -->', '<!-- ===== 顶部标题区 ===== -->')
# 标题中的装饰字符（title-emblem span）
c = c.replace('title-emblem">' + p + '/span>', 'title-emblem">◆</span>')
# 右上角时间注释
c = c.replace('<!-- ===== 右上角时间日' + p + '===== -->', '<!-- ===== 右上角时间日期 ===== -->')
# 扫描线动画注释
c = c.replace('<!-- ===== 扫描线动' + p + '===== -->', '<!-- ===== 扫描线动画 ===== -->')
# 模式选择注释
c = c.replace('<!-- ===== 模式未选择：展示两个入' + p + '===== -->', '<!-- ===== 模式未选择：展示两个入口 ===== -->')
# 电脑图标 emoji 后带损坏+/div>
c = c.replace('<div class="mode-icon">🖥' + p + '/div>', '<div class="mode-icon">🖥</div>')
# 管理端名称
c = c.replace('<div class="mode-name">管理' + p + '/div>', '<div class="mode-name">管理端</div>')
# 描述中的待办
c = c.replace('管理会议、归档、待' + p + '/div>', '管理会议、归档、待办</div>')
# 会议端名称
c = c.replace('<div class="mode-name">会议' + p + '/div>', '<div class="mode-name">会议端</div>')
# 纪要审签
c = c.replace('签到、材料、纪要审' + p + '/div>', '签到、材料、纪要审签</div>')
# 返回按钮 (← 是 U+2190，3字节)
c = c.replace('>' + p + '返回</el-button>', '>← 返回</el-button>')
# 管理端登录标题
c = c.replace('<h2 class="login-title">管理端登' + p + '/h2>', '<h2 class="login-title">管理端登录</h2>')

# ===== 2. 表单 placeholder 修复 =====
# 请输入账号（损坏吃掉了 号"）
c = c.replace('placeholder="请输入账' + p + ' prefix-icon="User"', 'placeholder="请输入账号" prefix-icon="User"')
# 请输入密码（出现多次，逐个修复）
c = c.replace('placeholder="请输入密' + p + ' prefix-icon="Lock" size="large" show-password />', 
              'placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />', 1)
# 请输入真实姓名
c = c.replace('placeholder="请输入真实姓' + p + ' prefix-icon="UserFilled"', 
              'placeholder="请输入真实姓名" prefix-icon="UserFilled"')
# 请输入邮箱
c = c.replace('placeholder="请输入邮' + p + ' prefix-icon="Message"', 
              'placeholder="请输入邮箱" prefix-icon="Message"')
# 第二个密码输入框
c = c.replace('placeholder="请输入密' + p + ' prefix-icon="Lock" size="large" show-password />', 
              'placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />', 1)

# ===== 3. 按钮文字（两个连续损坏 = 两个汉字）=====
# 登录按钮
c = c.replace('@click="handleLogin">\n                  ' + p + p + '\n                </el-button>',
              '@click="handleLogin">\n                  登录\n                </el-button>')
# 注册按钮
c = c.replace('@click="handleRegister">\n                  ' + p + p + '\n                </el-button>',
              '@click="handleRegister">\n                  注册\n                </el-button>')

# ===== 4. 会议室布局数据修复 =====
# 第一个和第二个 '3X号会议室' 键名（不同房间）
c = c.replace("'3" + p + "号会议室'", "'3甲号会议室'", 1)
c = c.replace("'3" + p + "号会议室'", "'3乙号会议室'", 1)

# 会议桌标签（多次出现，全部替换）
c = c.replace("label: '会议" + p, "label: '会议桌'")

# 主席台
c = c.replace("label: '主席" + p, "label: '主席台'")

# 5楼大会议室
c = c.replace("'5楼大会议" + p, "'5楼大会议室'")

# 1楼多功能厅
c = c.replace("'1楼多功能" + p, "'1楼多功能厅'")

# 报告厅
c = c.replace("'报告" + p, "'报告厅'")

# ===== 5. 座位编号 label 修复 =====
# 座位号格式 'N号' where 号' 被吞
for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
    # 单引号和'号'都被吃掉
    old = "label: '" + n + p
    new = "label: '" + n + "号'"
    c = c.replace(old, new)

# ===== 6. 星期数组修复 =====
# weekMap = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六']
# index 0 = 日，index 1 = 一（完好），index 2~6 = 二~六
weekdays_fix = ['日', '二', '三', '四', '五', '六']
for day in weekdays_fix:
    c = c.replace("'星期" + p, "'星期" + day + "'", 1)

# ===== 7. 表单验证消息修复 =====
c = c.replace("message: '请输入密" + p + ", trigger:", "message: '请输入密码', trigger:")
c = c.replace("message: '请输入真实姓" + p + ", trigger:", "message: '请输入真实姓名', trigger:")
c = c.replace("message: '请输入邮" + p + ", trigger:", "message: '请输入邮箱', trigger:")
c = c.replace("message: '邮箱格式不正" + p + ", trigger:", "message: '邮箱格式不正确', trigger:")
# 密码不少于N位（两个连续损坏: 于 + 6位）
c = c.replace("message: '密码不少" + p + p + ", trigger:", "message: '密码不少于6位', trigger:")

# ===== 8. ElMessage 错误提示 =====
c = c.replace("'未找到进行中的会议，请稍候重" + p + ")", "'未找到进行中的会议，请稍候重试')")

# ===== 9. 绘图函数注释修复（低优先级）=====
# 倾斜约45度
c = c.replace('ctx.rotate(-0.45) // 倾斜' + p + '5°', 'ctx.rotate(-0.45) // 倾斜约45°')
# 大面积星云雾气
c = c.replace('// ---- 大面积星云雾' + p + '----', '// ---- 大面积星云雾气 ----')
# 冷蓝
c = c.replace('色温随机：冷' + p + '/ 暖黄', '色温随机：冷蓝 / 暖黄')
# 白色注释
c = c.replace("'240,245,255'                    // " + p + "\n    ctx.beginPath()",
              "'240,245,255'                    // 白\n    ctx.beginPath()")
# 十字准星注释
c = c.replace('// 柔和圆形光晕，不是十' + p + '\n    const glow',
              '// 柔和圆形光晕，不是十字\n    const glow')

# ===== 10. CSS/SCSS 注释修复 =====
# 多行注释头部
c = c.replace('深蓝科幻军事' + p + '—' + p + '复刻登录' + p,
              '深蓝科幻军事风 — 复刻登录页')
# 颜色变量注释
c = c.replace('// ===== 颜色变量（仅本页' + p + '=====',
              '// ===== 颜色变量（仅本页）=====')
# 顶部标题区 CSS 注释
c = c.replace('/* ===== 顶部标题' + p + '===== */', '/* ===== 顶部标题区 ===== */')
# 右上角时间日期 CSS 注释
c = c.replace('/* ===== 右上角时间日' + p + '===== */', '/* ===== 右上角时间日期 ===== */')
# 扫描线 CSS 注释
c = c.replace('/* ===== 扫描' + p + '===== */', '/* ===== 扫描线 ===== */')
# 会议端自动关联样式注释
c = c.replace('/* 会议端自动关联样' + p + '*/', '/* 会议端自动关联样式 */')

after_count = c.count(p)
print(f'修复前：{before_count} 处损坏')
print(f'修复后：{after_count} 处损坏')

with open(r'E:\event-intelligent\frontend\src\views\Login.vue', 'w', encoding='utf-8') as f:
    f.write(c)
print('Login.vue 写入完成')
