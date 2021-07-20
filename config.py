headers = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
cookies = {
    "T_WM": "23010681771",
    "SCF":
        "Apy097ZCCps4raq8Vak6EclcDTnVbRHotrL1kjvg0HhijCiQ5tx1fjNRHoOOepPEF-LGgptwgd60d949_PPNL50.",
    "SUB":
        "_2A25N6V0LDeRhGeBP6VQS8C3JyD-IHXVvEmNDrDV6PUJbktANLVankW1NRWejPTCpa09SvJ7HnWZJTrmZdo8PXaum",
    "SUBP":
        "0033WrSXqPxfM725Ws9jqgMF55529P9D9W5v1ED0B0LiqpSlMv3MxhXd5NHD95QceKzce050SKe0Ws4DqcjG9NHrUgUfq7tt",
    "MLOGIN": "1",
    "M_WEIBOCN_PARAMS":
        "oid%3D4655386890338872%26luicode%3D10000011%26lfid%3D231093_-_selffollowed%26fid%3D231093_-_selffollowed%26uicode%3D10000011",
    "XSRF-TOKEN": "be39c4",
    "WEIBOCN_FROM": "1110006030"
}
proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
}

"""followers api返回json
{
    ‘ok': 1,
    'data': {
        'cardlistInfo'：{
        }
    }，
    ’cards': [
    {}
    {'card_type':xx,
     'item_id':xx,
     'card_group':[{follower1}, {follower2}, {follower3}]}
    ]
}
"""

info_url = "https://m.weibo.cn/profile/info?uid={id}"
follower_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{id}"
fans_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{id}"
