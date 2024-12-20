import logging
import os.path

import colorama
import colorlog
import jinja2
from colorama import Fore

__doc__ = """
日志记录，输出到控制台和文件。BaseScreen 为基类，Output 类继承该类并重写
写入文件功能暂未实现

Example:
    output.info("information")
    output.info(f"test: {output.RED}information{output.RESET}")
    output.success("success")
    output.error("error")
"""

from prettytable import PrettyTable
from utils import module_base_class
from utils.consts import AllPluginTypes


def print_centralization_help():
    from utils import read_version

    print(
        f"""
   █████████    █████████                  █████  ███   █████
  ███░░░░░███  ███░░░░░███                ░░███  ░░░   ░░███
 ███     ░░░  ░███    ░███  █████ ████  ███████  ████  ███████
░███          ░███████████ ░░███ ░███  ███░░███ ░░███ ░░░███░
░███          ░███░░░░░███  ░███ ░███ ░███ ░███  ░███   ░███
░░███     ███ ░███    ░███  ░███ ░███ ░███ ░███  ░███   ░███ ███
 ░░█████████  █████   █████ ░░████████░░████████ █████  ░░█████
  ░░░░░░░░░  ░░░░░   ░░░░░   ░░░░░░░░  ░░░░░░░░ ░░░░░    ░░░░░
                                                       {read_version()}


{output.RED}全局参数{output.RESET}
    --debug    开启调试模式
    --thread   设置线程数 (scan 模式下生效)
    --save     结果保存文件名

{output.RED}可用模块{output.RESET}:
    {'':^4}{output.YELLOW}{' '.join(module_base_class.keys())}{output.RESET}
{output.RED}AD{output.RESET}:
   {output.YELLOW}scan{output.RESET}
       [-h] (--all | --no-all | --plugin PLUGINS [PLUGINS ...]) [-U USERNAME] [-P PASSWORD] -D DOMAIN_FQDN [--dc-ip DOMAIN_IP]

       --all       加载全部扫描插件
       --plugin PLUGINS [PLUGINS ...]
                   选择一个/多个扫描插件，输入插件别名，程序会寻找别名对应的插件
       -U USERNAME, --username USERNAME
                   指定域控用户名 (大部分扫描插件需要)
       -P PASSWORD, --password PASSWORD
                   密码
       -D DOMAIN_FQDN, --domain DOMAIN_FQDN
                   指定域控 FQDN (DC01.test.lab)
       --dc-ip DOMAIN_IP
                   手动指定域控 ip 地址
   {output.YELLOW}exploit{output.RESET}
       (程序设计) 每个漏洞利用插件都有自己的参数，使用 -h/--help查看对应参数

{output.RED}Exchange{output.RESET}:
   ....

----

{output.RED}Example{output.RESET}:
    {output.YELLOW}AD{output.RESET}:
        列出扫描插件信息
            {output.GREEN}./main.py AD scan -h{output.RESET}
        列出漏洞利用插件信息
            {output.GREEN}./main.py AD exploit -h{output.RESET}
            {output.GREEN}./main.py AD exploit kerb_ue -h{output.RESET}
        使用全部扫描插件
            {output.GREEN}./main.py AD scan --all -D dc.test.lab --dc-ip 20.0.0.100 -U administrator -P 123.com{output.RESET}
        使用全部扫描插件，并指定线程，保存结果到文件
            {output.GREEN}./main.py --thread 50 --save ad_result.html AD scan --all -D dc.test.lab --dc-ip 20.0.0.100 -U administrator -P 123.com{output.RESET}
        使用指定的扫描插件
            {output.GREEN}./main.py AD scan --plugin no_recycle_bin_dc nver_expire_priv_act -D dc.test.lab --dc-ip 20.0.0.100 -U administrator -P 123.com{output.RESET}
"""
    )
    exit(0)


class BaseScreen:
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Fore.RESET

    prefix_info = f"{BLUE}[*]"
    prefix_success = f"{GREEN}[+]"
    prefix_error = f"{RED}[-]"
    prefix_debug = f"{CYAN}[*]"

    log_color = {
        "DEBUG": "blue",
        "INFO": "blue",
        "WARNING": "blue",
        "ERROR": "blue",
        "CRITICAL": "blue",
    }

    def __init__(
        self,
        fmt: str = "%(asctime)s %(filename)s:%(lineno)d %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M",
    ):
        # 初始化颜色
        colorama.init(autoreset=True)

        # 屏幕输出器 - 基本输出器
        # self.screenFormat = logging.Formatter(fmt=fmt, datefmt=datefmt)
        self.screenFormat = colorlog.ColoredFormatter(
            fmt="%(log_color)s" + fmt, datefmt=datefmt, log_colors=self.log_color
        )
        self.screenHandle = logging.StreamHandler()
        self.screenHandle.setFormatter(self.screenFormat)
        self.screenLogger = logging.getLogger("screen")
        self.screenLogger.setLevel(logging.INFO)
        self.screenLogger.addHandler(self.screenHandle)

    def info(self, string):
        self.screenLogger.info(f"{self.prefix_info} {string}{output.BLUE}")

    def success(self, string):
        self.screenLogger.info(f"{self.prefix_success} {string}")

    def error(self, string):
        self.screenLogger.error(f"{self.prefix_error} {string}")

    def debug(self, string):
        self.screenLogger.debug(f"{self.prefix_debug} {string}")

    def open_debug(self):
        self.screenLogger.setLevel(logging.DEBUG)


class Output(BaseScreen):
    def __init__(self):
        super().__init__(fmt="%(message)s")
        self.save = "results.html"
        self.isDebug = False

    def print_simple_help(self, mod=""):
        if mod == "all":
            print_centralization_help()

        if mod == "":
            print(f"valid module:")
            [print(f'{"":^4}{x}') for x in module_base_class.keys()]
        else:
            print(f"{mod} sub command:\n" f"{'':^4}scan\n" f"{'':^4}exploit")

    def show_results(self, results: dict, scan_type) -> None:
        """
        以表格形式输出结果
        :param results: 收集的结果，字典
        :return: None
        """

        # root 节点
        success_plugin_nodes = []
        title = ["Plugin Name", "Display", "Status", "Result"]
        run_status_string = ["Failed", "Success", "Error"]

        total = {"total": len(results), "s_count": 0, "f_count": 0, "e_count": 0}

        html_template_data = {}

        result_table = PrettyTable(title)
        # 设置对齐
        result_table.align["Plugin Name"] = "l"
        result_table.align["Display"] = "l"
        result_table.align["Status"] = "l"
        result_table.align["Result"] = "l"
        # 消除边框
        result_table.border = False

        for plugin_name, v in results.items():

            status = "Failed"
            try:
                status = run_status_string[v["results"]["status"]]
            except TypeError as e:
                total["e_count"] += 1

            if status != "Failed":
                # 记录成功和错误结果
                result_value = ""
                try:
                    for ins in v["results"]["data"]["instance_list"]:
                        for k, val in ins.items():

                            result_value += f"{k}: {str(val)}\n"
                except TypeError:
                    status = run_status_string[-1]
                    result_value = v["results"]
                except KeyError:
                    result_value = str(v["results"]["error"])

                if len(result_value) > 50:
                    result_value = "..."
                result_table.add_row(
                    [plugin_name, v["display"], status, result_value.strip()]
                )

                # html 只显示成功的结果
                if (
                    status == "Success"
                    and len(v["results"]["data"]["instance_list"]) > 0
                ):
                    html_template_data[plugin_name] = v

            # 添加攻击链节点
            if status == "Success":
                success_plugin_nodes.append(v["alias"])
                total["s_count"] += 1

            if status == "Failed":
                total["f_count"] += 1

        output.success(f"script results{output.RESET}\n" f"{result_table}\n")

        # Load the HTML template using Jinja2
        templateLoader = jinja2.FileSystemLoader(searchpath="./utils/template")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template("temp.html")

        # Render the template with the data
        outputText = template.render(data=html_template_data)

        # Print the final HTML code
        if not os.path.exists("result"):
            os.makedirs("result")

        with open(f"result/{self.save}", "w", encoding="utf-8") as f:
            f.write(outputText)

        output.success(f"details are saved to result/{self.save}")

        if scan_type == AllPluginTypes.Exploit:
            self.info("Attack chains:")
            self.debug(f"get attack root chain node: {success_plugin_nodes}")

            from utils.attack_chain import AttackChains

            a_chains = AttackChains()
            for n in success_plugin_nodes:
                a_chains.match(n)
            a_chains.print_chains()

        output.info(
            f"Total:\n"
            f"{'':^4}Number of plugin executions: {total['total']}\n"
            f"{'':^4}Number of plugin hits:       {total['s_count']}\n"
            f"{'':^4}Number of plugin misses:     {total['f_count']}\n"
            f"{'':^4}Number of plugin runtime errors:  {total['e_count']}\n"
        )


output = Output()
