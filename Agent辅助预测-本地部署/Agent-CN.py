import os
import joblib
import pandas as pd
from docx import Document
from openpyxl import Workbook
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from sklearn.preprocessing import StandardScaler
import numpy as np
import json
from dotenv import load_dotenv
from langchain_community.llms import Ollama




# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Robot:
    def __init__(self):
        # 初始化大模型
        self.model = Ollama(model="deepseek-r1:14b")
        self.row = 1

    def qiye_data(self,dataset_xlsx:str) -> str:
        """
        进行企业资产评估时，必须调用该工具，以获得用户待测试数据的详细描述，你需要详细理解待测试数据的内容，以便根据历史评审经验和模型给出的初步评审结果对最终评审金额给出调整建议。
        :return: 待测试数据的数据内容
        """
        def extract_features(dataset):
            data = {
                # 项目基础信息
                "项目编号": dataset["项目编号"].values[0],
                "企业名称": dataset["企业名称"].values[0],
                "项目经理A": dataset["项目经理A"].values[0],
                "申请金额": f"{dataset['申请金额'].values[0]}万元",
                "申请期限": f"{dataset['申请期限'].values[0]}年",
                "月还款方案": f"{dataset['申请还款方案还款方式（月还本息之和。单位：万元）'].values[0]}万元",

                # 实控人信息
                "实控人性别": f"{dataset['实控人性别'].values[0]}（0=女，1=男）",
                "文化程度": dataset["实控人文化程度"].values[0],
                "婚姻状态": f"{dataset['婚姻状态'].values[0]}（0=未婚，1=已婚）",
                "居住类型": f"{dataset['居住场所类型'].values[0]}（0=自购，1=租赁）",
                "本地居住": f"{dataset['本地居住时间（年）'].values[0]}年",

                # 经营特征
                "主营业务": dataset["主营业务（填写文字信息）"].values[0],
                "所属行业": dataset["所属行业（大类）"].values[0],
                "从业年限": f"{dataset['借款人从业限（包括和当前从事行业相关的学习、打工期间）'].values[0]}年",
                "外贸类型": f"{dataset['是否外贸型'].values[0]}（0=否，1=是）",
                "谨慎行业": f"{dataset['是否属于谨慎介入行业'].values[0]}（0=否，1=是）",
                "员工人数": dataset["企业雇佣人数（不含借款人家庭成员）"].values[0],
                "经营场所": f"{dataset['经营场所类型'].values[0]}（0=自有，1=租赁）",
                "月租金": f"{dataset['场地月租金（万元）'].values[0]}万元",

                # 财务数据
                "月均余额": f"{dataset['月均余额（万元）'].values[0]}万元",
                "日均余额": f"{dataset['日均余额（万元）'].values[0]}万元",
                "货币资金": f"{dataset['上会时点货币资金（万元）'].values[0]}万元",
                "应收账款": f"{dataset['上会时点应收账款（万元）'].values[0]}万元",
                "存货": f"{dataset['上会时点存货（万元）'].values[0]}万元",
                "应付账款": f"{dataset['上会时点应付帐款（万元）'].values[0]}万元",
                "总资产": f"{dataset['总资产（万元）'].values[0]}万元",
                "总负债": f"{dataset['总负债（万元）'].values[0]}万元",
                "净资产": f"{dataset['净资产（万元）'].values[0]}万元",
                "年销售": f"{dataset['年销售收入（万元）'].values[0]}万元",
                "月净收益": f"{dataset['月净收益（万元）'].values[0]}万元",

                # 风险指标
                "销售负债率": f"{dataset['销售负债率（%）'].values[0]}%",
                "资产负债率": f"{dataset['资产负债率（%）'].values[0]}%",
                "原还款额": f"{dataset['原贷款的月还款本息（万元）'].values[0]}万元",
                "新增还款额": f"{dataset['加上本笔贷款的月还本息（万元）'].values[0]}万元",
                "收益还款比": dataset["月净收益/月还本息比值"].values[0],

                # 担保信息
                "房产抵押": f"{dataset['房产抵押 如有，填写房产评估值（万元）'].values[0]}万元" if
                dataset['房产抵押 如有，填写房产评估值（万元）'].values[0] else "无",
                "设备抵押": f"{dataset['设备抵押  如有，请填写设备净值（万元）'].values[0]}万元" if
                dataset['设备抵押  如有，请填写设备净值（万元）'].values[0] else "无",
                "担保人": f"{dataset['是否增加了有效担保人（兄弟姐妹、上下游、合作伙伴、其他）'].values[0]}（0=否，1=是）",

                # 文本信息（保留原始格式）
                "利润去向": dataset["近三年利润去向描述"].values[0].replace('"', ''),
                "家庭情况": dataset["家庭成员及情况"].values[0].replace('"', ''),
                "商业模式": dataset["商业模式"].values[0].replace('"', ''),
                "风险分析": dataset["项目结论"].values[0].replace('"', '')
            }

            # 处理空值
            for k, v in data.items():
                if pd.isna(v) or str(v) == 'nan':
                    data[k] = "无记录"

            return data

        def generate_report(data):
            template = f"""
        **企业信贷分析报告**

        一、基础信息
        项目编号：{data['项目编号']}
        企业名称：{data['企业名称']}（项目经理：{data['项目经理A']}）
        申请金额：{data['申请金额']}，期限：{data['申请期限']}
        还款方案：每月偿还本息 {data['月还款方案']}

        二、实控人背景
        1. 性别：{data['实控人性别']}
        2. 文化程度：{data['文化程度']}
        3. 婚姻状态：{data['婚姻状态']}
        4. 居住情况：{data['居住类型']}，本地居住 {data['本地居住']}

        三、经营状况
        1. 主营业务：{data['主营业务']}（行业分类：{data['所属行业']}）
        2. 从业年限：{data['从业年限']}
        3. 经营场所：{data['经营场所']}，月租金 {data['月租金']}
        4. 员工规模：{data['员工人数']}人（不含家庭成员）

        四、财务概况（单位：万元）
        1. 资金状况：
           - 月均余额：{data['月均余额']}
           - 货币资金：{data['货币资金']}
           - 应收账款：{data['应收账款']}
           - 应付账款：{data['应付账款']}

        2. 资产状况：
           - 总资产：{data['总资产']}
           - 净资产：{data['净资产']}
           - 年销售额：{data['年销售']}
           - 月净收益：{data['月净收益']}

        五、风险指标
        1. 负债情况：
           - 资产负债率：{data['资产负债率']}
           - 销售负债率：{data['销售负债率']}
           - 现有月还款：{data['原还款额']} → 新增后：{data['新增还款额']}

        2. 担保措施：
           - 房产抵押：{data['房产抵押']}
           - 设备抵押：{data['设备抵押']}
           - 新增担保人：{data['担保人']}

        六、深度分析
        1. 利润去向：
        {data['利润去向']}

        2. 家庭情况：
        {data['家庭情况']}

        3. 商业模式：
        {data['商业模式']}

        4. 风险分析：
        {data['风险分析']}

        **综合评估结论**
        请基于上述信息，重点分析：
        1. 租金收入稳定性与还款能力相关性
        2. 多子女背景对代偿能力的影响
        3. 私烟经营的法律风险
        4. 网贷置换的合规性审查
        """
            # 清理空行并保留缩进
            return '\n'.join([line for line in template.split('\n') if line.strip()])

        #调取第a行
        a = self.row
        dataset = pd.read_excel(dataset_xlsx)
        row = dataset.iloc[[a]] # 获取单行数据
        features = extract_features(row)
        report = generate_report(features)
        return report

    def jingyan_tool(self, file_path: str) -> str:
        """
        进行企业资产评估时，必须调用该工具，从Word文档中读取所有经验文本内容，并将其返回作为参考，对评估金额给出调整建议。
        :return: 文档中的所有经验文本内容
        """
        try:
            # 假设Word文档路径为 "./experience_data.docx"
            doc = Document(file_path)
            # 读取所有段落文本，并将它们合并成一个字符串
            text_content = "\n".join([para.text for para in doc.paragraphs])
            return text_content
        except Exception as e:
            return f"读取文档时出错: {e}"

    def pinggu_qiye(self,dataset_xlsx: str) -> str:
        """
               根据输入的企业待评估的特征数据，调用机器学习模型预测企业的评估结果。
               :param data: 企业待评估的特征数据,excel形式的数据
               :return: 企业的资产评估的结果
               """
        dataset = pd.read_excel(dataset_xlsx)
        # 调取第a行数据
        a = self.row
        dataset = dataset.iloc[[a]]
        dataset["实控人文化程度"] = dataset["实控人文化程度"].replace(
            {"博士后": 7, "博士": 6, "硕士": 5, "本科": 4, "专科": 3, "大专": 3, "中专": 2, "高中": 2, "职高": 1.5,
             "初中": 1, "小学": 0})
        columns_to_drop = [
            '主营业务（填写文字信息）',
            '近三年利润去向描述',
            '其他软信息描述',
            '学习及工作经历',
            '家庭成员及情况',
            '商业模式',
            '反担保措施',
            '贷款用途描述',
            '项目结论'
        ]
        dataset.drop(columns=columns_to_drop, inplace=True)
        dataset["所属行业（大类）"] = dataset["所属行业（大类）"].replace(
            {"制造业": 9, "农业": 8, "贸易": 7, "零售业": 6, "教育业": 5, "建筑业": 4, "公安安全管理业": 3, "服务业": 2,
             "纺织业": 1, "餐饮业": 0})
        dataset = dataset.fillna(0)

        try:
            scaler_X = joblib.load('/Users/leo/研究生/资产评估/汕头合作/线下交流/scaler_X.pkl')
            scaler_y = joblib.load('/Users/leo/研究生/资产评估/汕头合作/线下交流/scaler_y.pkl')
            xgb_model = joblib.load('/Users/leo/研究生/资产评估/汕头合作/线下交流/best_model.pkl')
        except FileNotFoundError as e:
            return f"模型文件未找到: {e}"
        except Exception as e:
            return f"加载模型时出错: {e}"

        X_new = dataset[
            ['申请金额', '净资产（万元）', '总资产（万元）', '核心资产（固定资产表+货币资金）（万元）', '上会时点存货（万元）',
             '借款人从业限（包括和当前从事行业相关的学习、打工期间）', '本地居住时间（年）', '上会时点应收账款（万元）',
             '年销售收入（万元）', '用电量（/）', '总负债（万元）', '申请还款方案还款方式（月还本息之和。单位：万元）']]
        X_new_scaled = scaler_X.transform(X_new)
        predicted_tvbn = xgb_model.predict(X_new_scaled)
        predicted_tvbn = scaler_y.inverse_transform(predicted_tvbn.reshape(-1, 1))[0][0]
        predicted_tvbn = predicted_tvbn.tolist()
        return predicted_tvbn
    def batch_predict(self, dataset_xlsx: str, history_file: str):
        """批量预测测试集并保存结果到Excel"""
        # 加载历史经验
        history_data = self.jingyan_tool(history_file)

        # 提供给大模型的提示
        prompt = f"""                
                **系统角色：**
                ```
                您是一位经验丰富的中小微企业融资担保评估专家，擅长分析企业财务数据和描述信息，识别影响融资担保评估准确性的关键因素。
                ```
            你的任务是：

            1. 根据用户的问题，调用适当的工具（如RAG工具或API），提供最准确的企业资产预测和查询信息。若用户要进行融资担保评估，则首先要接收模型对该企业的融资担保评估的预测结果，还要根据企业的信息，和你的知识储备，
            以及下面给出的历史评估经验，综合给用户提意见，即是否向该企业贷款或贷款金额是否合适或还需要重点关注该企业的哪些问题。注意对于评估经验文本要仔细学习，按照每条的要求对输入的数据进行分析，将分析过程以及最终结果和结合模型给出的最终建议的评估金额全部输出，要求非常的详细。
            注意：机器学习模型给出的本笔贷款可申请金额的参考价值占到80%，要在预测结果的基础上，结合经验和相关知识等，判断是否批准这笔贷款担保申请。
            历史评估经验如下："{history_data}".  
            2. 在回答时：
                - 保持语气温和、友好，并提供有用的建议。
                - 请分步骤说明复杂的查询结果，必要时详细解释背景知识。
                - 确保答案简洁、清晰，但必要时可以详细解释背景知识。

            3. 处理特殊情况
                - 如果数据不可用或无法确定结果，请礼貌地告知用户原因，并建议用户提供更多信息（如具体企业ID）。
                - 如果用户输入的格式不正确，请友好地提醒并提供正确的输入格式。
            4. **应用总结经验进行新数据评估：**
    ·		•步骤：
                分析新企业的描述信息，聚焦与历史错误预测相关的特征。
                依次检索以往数据与经验文档，检查可参照的类似案例和核心特征组合。
                结合特征贡献度排名，若在特征间出现冲突则倾向依赖排名更高的特征做最终判定。
                做出结论：
    •		如果对模型预测完全认可，输出“建议批准本笔贷款担保申请”；
    •		如果无法确定或认为模型的预测结果有误，输出“建议暂缓本笔贷款担保申请”。

        
            **注意事项：**
            1. **逐步推理（思维链）：**
                - 在内部进行详细分析和推理，但最终回答中不展示这些步骤。
            2. **准确性和专业性：**
                - 完全依赖于历史数据中总结的规律和经验，避免主观猜测。
            3. **明确和绝对的结论：**
                - 结论应明确无误，避免使用模棱两可的语言。
            4. **提升模型准确率：**
                - 关注预测模型的86%准确率，因此要有百分百的把握给出结论，不怕思考时间长，要反复检查思考最后再得出结论。
            5. **重点挖掘误差原因：**
                - 深入分析导致预测错误的具体特征或特征组合，提出避免误差的建议。
        
        """

        # 加载测试数据
        try:
            dataset = pd.read_excel(dataset_xlsx)
            # 调取第a行数据
            a = self.row
            dataset = dataset.iloc[[a]]
            logger.info("成功加载测试数据。")
        except Exception as e:
            logger.error(f"加载测试数据时出错：{e}")
            return
        results = []

        try:

            # 使用所有模型进行加权预测
            model_result = self.pinggu_qiye(dataset_xlsx)
            qi_ye_data = self.qiye_data(dataset_xlsx)

            text = f"""
            新待判断数据：
            预测模型对该公司的预测结果如下： {model_result}万元，该公司的数据如下：{qi_ye_data}。
            注意：机器学习模型给出的本笔贷款可申请金额的参考价值占到80%，要在预测结果的基础上，结合经验和相关知识等，判断是否批准这笔贷款担保申请。
            “请按照给出的说明进行操作。一步一步地仔细分析所提供的数据（内部分析，不要暴露你的思维链），然后按照下列要求的格式提出你的最终结论。” 
            **最终输出格式需要包含以下5点内容：**
            ```
            - 1.**该企业申请的评估金额：{dataset['申请金额'].values}万元 （样本中申请金额的值）
                    期限：{dataset['申请期限'].values}年   （样本中申请期限的值）
                    每月偿还本息： {dataset['申请还款方案还款方式（月还本息之和。单位：万元）'].values}万元   （样本中申请还款方案还款方式（月还本息之和。单位：万元）的值）
              （这部分根据输入的样本中内容输出）
              **
            - 2.**模型对该企业的评估资产的预测结果： {model_result}万元    ** （这部分根据给出的模型预测结果的值输出）
            - 3.**通过学习到的经验对模型预测结果判断的最终结论：** [建议批准本笔贷款担保申请/ 建议暂缓本笔贷款担保申请]  （这部分根据判断的结果输出）
            - 4. [若第三点最终评审结论为：‘建议批准本笔贷款担保申请’ 。则按照下列格式输出最终判断的结论，批准金额按照申请金额批准]
                ** 最终批准结果为：
                 - **批准金额： x万元
                 - **期限： x年
                 - **每月偿还本息： x 万元
                （这部分根据判断的结果输出）
                /[若最终评审结论为：‘建议暂缓本笔贷款担保申请’，则继续输出第五点内容]
                ** 
            - 5.**结论摘要：** 详细说明判断的依据和关键因素，并且给出详细建议和评审理由。
            ```
            """
            True_prediction = dataset['过会金额（万元）'].values
            # True_prediction = ['0']
            # 调用大模型进一步评估

            try:
                final_decision = self.model.invoke([
                    # 回答1
                    SystemMessage(content = prompt),
                    HumanMessage(content=f"输入数据: {text}。")
                    # 回答2
                    # HumanMessage(content=f"系统信息：{prompt},输入数据: {text}。")
                ])
                final_judgment = final_decision
            except Exception as e:
                logger.error(f"调用大模型时出错：{e}")
                final_judgment = "大模型评估失败"

            results.append({
                "真实评估金额":True_prediction,
                "企业数据": text,
                "模型预测金额": model_result,
                "大模型判断": final_judgment
            })
            logger.info(f"真实评估金额：{True_prediction},模型预测金额: {model_result},大模型判断: {final_judgment}")

        except Exception as e:
            logger.error(f"处理数据时出错：{e}")



if __name__ == '__main__':
    robot = Robot()
    robot.batch_predict(
        dataset_xlsx="/Users/leo/研究生/资产评估/汕头合作/线下交流/黑箱测试集.xlsx",
        history_file="/Users/leo/研究生/资产评估/汕头合作/线下交流/贷款评审要素_总结版.docx",
    )
