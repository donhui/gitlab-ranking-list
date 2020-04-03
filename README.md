## 背景
在管理/维护 gitlab 服务的过程中，总会思考如下问题

例如：为什么仓库很大？是代码中包含二进制？还是分支过多？或者是其它原因？

于是，便想通过数据分析，发现 gitlab 使用中的反模式，从而为规范使用行为提供数据支持

## gitlab 排行榜
仓库大小排行榜（排除掉 forked 仓库），按仓库大小降序排列，以网页表格的形式展示 TOP 100

## 环境要求
Python 3.4+

备注：如果使用的是 Python 2.7，请查看相关历史 [tag](https://github.com/donhui/gitlab-ranking-list/releases/tag/python-2-release)

## 使用方式
- 安装依赖：`pip install -r requirements.txt`
- 修改配置：修改 `settings.py` 中的 gitlab 相关认证信息
- 运行脚本：使用 python 运行 `gitlab-ranking-list.py`
- 查看结果：脚本执行完毕后，会生成 `gitlab-ranking-list.html`，可以用浏览器打开查看

备注：仓库数量越多，脚本执行的时间会越长
