# settings.py
BASE_URL = "https://k.kuaishou.com/official.html#/"
LOGIN_URL = BASE_URL

# 列表页（示例 accountId）
LIST_URL  = "https://k.kuaishou.com/?__accountId__=9964030#/star_plaza/video?__accountId__=9964030"

                      # 首次登录建议 False（有头方便手动验证）
STORE_DIR = "./.pw-store"
# 存储目录换成你项目里的新文件夹，不要用 Default
USER_DATA_DIR = "./pw-profile"
PROFILE_NAME = "Default"   # 这里随便填，不会用到
HEADLESS = False
PROXY = None                           # e.g. "http://user:pass@host:port"
TIMEOUT = 30000                        # ms（全局默认超时）
SCREEN_DIR = "./debug_screens"

# 登录（可空：留空=完全手动输入账号密码）
ACCOUNT = ""   # "your_email_or_mobile"
PASSWORD = ""  # "your_password"

# 列表页控制
MAX_PAGES_PER_RUN = 1   # 一次最多翻多少页
START_PAGE = 1           # 起始页（要从 101 开始就改这里）
MAX_ITEMS_PER_PAGE = 2
# 每页最多采多少条，None=全采

# 输出 Excel
OUT_XLSX = "./data/kuaishou_sample.xlsx"

# 统一选择器（尽量使用文本锚点 + class 兜底）
SEL = {
    # 登录/进入客户
    "btn_i_am_customer_primary": "div[data-text='我是客户']",
    "btn_i_am_customer_fallback_text": "text=我是客户",
    "input_account": "input[placeholder='请输入手机号/邮箱']",
    "input_password": "input[placeholder='请输入密码']",
    "btn_login_candidates": [
        "button:has-text('登录')",
        "button:has-text('登 录')",
        "button:has-text('快手APP账号授权登录')",
        "text=登录"
    ],
    "login_ok_indicators": [
        "text=退出登录",
        "text=控制台",
        "text=首页"
    ],

    # 空间（页面1）— 找 User_... 条目并点“进入”
    "space_row_by_text": "text=User_1616377991157",
    "space_enter_link": "a.entry:has-text('进入')",

    # 页面2 → 找达人 → 短视频广场
    "tab_find_creator": "text=找达人",
    "cat_short_video_square": "text=短视频广场",

    # 列表页筛选：内容类型“三农”与“更多”
    "filter_group_content_type_anchor": "text=内容类型",
    "content_type_more_btn": "button.ant-btn.ant-btn-link.ant-btn-sm:has-text('更多')",
    "tag_sannong": "span.title___tcilP:has-text('三农')",

    # 排序（粉丝数）
    "sort_fans": "span.label___c1mIv:has-text('粉丝数')",

    # 列表条目标题（可点击进入详情）
    "item_title_span": "span.title___FsRl8",

    # 分页页码（示例：<a rel="nofollow">2</a>）
    "pager_link_fmt": "a[rel='nofollow']:has-text('{page}')",

    # 详情页第一部分
    "overview_number": "div.number___U3LOs > span, div.number___U3LOs",
    "audience_tag": "span.fansTag___BAtW2",

    # 传播表现
    "tab_spread_perf": "div[role='tab']:has-text('传播表现'), #rc-tabs-0-tab-2",
    "btn_last_30d": "text=近30天",
    "btn_last_90d": "text=近90天",
    "btn_personal_works": "span:has-text('个人作品')",
    "btn_juxing_works": "span:has-text('聚星作品')",
    "metric_name": "div.name___AHqKc",
    "metric_value_generic": "span[style*='Roboto-Medium']",
    "chart_subtitle": "div.chart-sub-title",
    "chart_tab_like": "div[role='tab']:has-text('点赞量'), #rc-tabs-4-tab-likeCnt",
    "chart_tab_comment": "div[role='tab']:has-text('评论量'), #rc-tabs-4-tab-commentCnt",
    "chart_tab_share": "div[role='tab']:has-text('分享量'), #rc-tabs-4-tab-forwardCnt",

    # 受众分析
    "tab_audience_analysis": "div[role='tab']:has-text('受众分析'), #rc-tabs-0-tab-3",
    "growth_title": "div.title___MsVbn",
    "growth_value": "span[style*='Roboto-Medium']",
    "btn_audience_portrait": "span:has-text('观众画像')",
    "btn_fans_portrait": "span:has-text('粉丝画像')",
    "gender_desc": "#fans-gender-chart-desc",
    "age_desc": "#fans-age-chart-desc",
}

