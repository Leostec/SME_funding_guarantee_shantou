# SME Funding Guarantee Shantou

​							[中文文档](./README-zh.md)

## Background

Small and medium-sized enterprises (SMEs) are a vital component of the national economy, playing an irreplaceable role in promoting economic growth, driving technological innovation, and increasing employment opportunities, while also serving as a source of vitality for the market economy. However, in recent years, SMEs have faced survival and development challenges due to issues such as difficulties in obtaining financing, weak market competitiveness, and low management capabilities. Due to their relatively small scale, incomplete credit records, and insufficient collateral, SMEs often struggle to secure adequate financial support from traditional institutions, which in turn affects their operational development and market competitiveness, becoming a key bottleneck restricting their growth (see Figure 1-1).

![Figure 1](./images/图1.jpg)  
*Figure 1-1: Ratio of SME Registrations to Cancellations*

To address the financing difficulties faced by SMEs, financing guarantees, as an effective risk-sharing mechanism, have become a primary tool to resolve these challenges. By introducing third-party guarantee institutions, credit enhancement is provided to SMEs, reducing the lending risks for financial institutions and thereby increasing the success rate of SME financing. However, in practice, the current financing guarantee business faces a series of issues, such as over-reliance on expert experience, lengthy review processes, strong subjectivity in evaluations, and difficulties in sharing guarantee data and experience. These problems severely limit the effective implementation of financing guarantee services and the financing accessibility for SMEs (see Figure 1-2).

![Figure 2](./images/图2.jpg)  
*Figure 1-2: SME Guarantee Process*

To overcome the shortcomings of traditional financing guarantee operations and improve the efficiency and accuracy of SME financing guarantees, exploring data-driven approaches for SME financing guarantee assessments has become particularly important. Data-driven methods can fully leverage historical data, using technologies such as machine learning to conduct comprehensive, objective, and precise evaluations of SMEs’ credit status, operational capabilities, and development prospects, thereby providing a scientific basis for financing guarantee decisions.

## Project 1 - LLM-Assisted Prediction
The specific framework of this project is shown in Figure 2, divided into two versions: API-based LLM invocation and locally deployed LLM.

**In the folders of both versions:**
- *RAG folder*: External knowledge base data - experiential data
- *scaler-model folder*: Normalization models and pre-trained prediction models
- *test_data folder*: Dataset to be tested

![img.png](./images/project1、2.png)  
*Figure 2: Algorithm Framework for Projects 1 and 2*

### Project 1-1 - Agent-Assisted Prediction - API
Using this project’s code, the official LLM API can be invoked to conduct financing guarantee assessments for SMEs in Shantou City (including structured data models, text data, and historical experience).  
`self.row` refers to selecting data from the x-th row of the test dataset.  
The API is stored in an `.env` file and called using `os`. Below is an example using DeepSeek:

```python
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('DeepSeek_trans_API')  # Set API key
os.environ["OPENAI_API_BASE"] = 'https://tbnx.plus7.plus/v1'  # Set URL address
```

### Project 1-2 - Agent-Assisted Prediction - Local Deployment
Using this project’s code, a locally deployed LLM can be used to conduct financing guarantee assessments for SMEs in Shantou City, ensuring data privacy and security with full localization.  
`self.row` refers to selecting data from the x-th row of the test dataset.

#### Steps to Deploy LLM Locally:
##### 1. Download and Install OLLAMA from the Official Website:
`https://ollama.com/download`

![img.png](./images/img.png)

##### 2. Download the LLM Model from the OLLAMA Website (e.g., DeepSeek-r1 14b Model)
Download the corresponding version from the official website:  
![img.png](./images/model.png)

Run in the terminal:  
`ollama run deepseek-r1:14b`

##### 3. Load the Model in the Code
```python
self.model = Ollama(model="deepseek-r1:14b")
```

## Project 3 - LEAF Algorithm - Feature-Enhanced Prediction
Using this code, feature expansion can be performed, followed by financing guarantee assessments for SMEs in Shantou City. The code framework is as follows:

![img.png](./images/project3.png)



[./README.md]: 
[./README-zh.md]: 
