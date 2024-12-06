# CAudit
>
> [!WARNING]
> 不支持 Python 12

## 描述

十大集权设施基线扫描工具

- AD、K8s、VCenter、Excange、JumpServer、齐治堡垒机、天钥堡垒机、Zabbix、阿里云、腾讯云、华为云
- 内置 AD 基线扫描脚本数量 80+、漏洞利用脚本数量 40+
- 内置 Exchange 基线扫描脚本 20 条，漏洞利用脚本 10 条
- 内置 VCenter 基线扫描脚本 15 条，漏洞利用脚本 18 条
- 内置 K8s 漏洞利用脚本 8 条、JumpServer 漏洞利用脚本 1 条、齐治堡垒机漏洞利用脚本 1 条
- 内置阿里云漏洞利用脚本 8 条、腾讯云漏洞利用脚本 6 条、华为云漏洞利用脚本 2 条
- 支持结果保存为 HTML 文件

## Example

显示全局参数和可用模块

```bash
./CAudit.py -h
```

![1.png](doc/1.png)

显示每个模块参数 (以 AD 为例)

```bash
./CAudit.py AD -h
```

![2.png](doc/2.png)

列出每个模块所有可用插件 (以 AD 为例)

```bash
./CAudit.py AD --list
```

![3.png](doc/3.png)

列出每个模块扫描/漏洞利用类型插件 (以 AD 为例)

```bash
./CAudit.py AD scan --list
./CAudit.py AD exploit --list
```

![4.png](doc/4.png)

使用全部扫描插件 (以 AD 为例)

```bash
CAudit.py --save ad_scan.html AD scan -u USER -p PASS -d DC.DOMAIN.COM --dc-ip 1.1.1.1 --all
```

![5.png](doc/5.png)

使用指定的扫描插件

```bash
./CAudit.py AD scan --plugin i_maq -d DC.DOMAIN.COM --dc-ip 1.1.1.1 --username USER --password PASS
```

![6.png](doc/6.png)

### 使用 Docker

使用前先拉最新镜像

`docker pull amulab/center`

运行

`docker run --rm -it amulab/center`

为了方便使用可以先设置别名

`alias center='docker run --rm -it amulab/center'`

再使用`center`命令运行
