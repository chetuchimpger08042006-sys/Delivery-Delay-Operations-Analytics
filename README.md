\# Delivery Delay \& Operations Analytics



\## 📦 Project Overview



\*\*Delivery Delay \& Operations Analytics\*\* is a data analytics and machine learning project that analyzes e-commerce delivery data to identify delivery delays, operational hotspots, and factors associated with late deliveries.



The project combines multiple Olist datasets at the order level and provides an interactive \*\*Streamlit dashboard\*\* for exploring delivery performance.



\---



\## 🎯 Project Objectives



\* Analyze delivery performance of e-commerce orders.

\* Calculate delivery delay and on-time delivery percentage.

\* Identify high-delay routes and operational hotspots.

\* Analyze delays by seller state, customer state, product category, weekday, and season.

\* Identify unusual monthly delivery-delay spikes.

\* Estimate delivery delay risk using a Decision Tree model.

\* Provide prioritized recommendations for improving delivery operations.

\* Build an interactive dashboard for business analysis.



\---



\## 🗂️ Dataset



This project uses the \*\*Brazilian E-Commerce Public Dataset by Olist\*\*.



The dashboard uses five CSV files:



\* `olist\_orders\_dataset.csv`

\* `olist\_order\_items\_dataset.csv`

\* `olist\_products\_dataset.csv`

\* `olist\_sellers\_dataset.csv`

\* `olist\_customers\_dataset.csv`



The dataset is not included in this repository. The Streamlit application allows the required CSV files to be uploaded through the sidebar.



\### Dataset Limitation



The Olist dataset does not contain:



\* Real carrier names

\* Actual warehouse IDs

\* Detailed delivery-event history



Therefore, this project uses:



\* \*\*Seller state\*\* as a warehouse proxy

\* \*\*Seller ID\*\* as a fulfilment proxy

\* \*\*Seller state → customer state\*\* as the delivery route



\---



\## 🔍 Project Workflow



\### 1. Data Preparation



The project combines order, item, product, seller, and customer information at the order level.



\### 2. Delivery Delay Calculation



Delivery delay is calculated as:



```text

Delay Days =

Actual Customer Delivery Date - Estimated Delivery Date

```



An order is considered \*\*late\*\* when:



```text

Delay Days > 0

```



An order is considered \*\*on time\*\* when:



```text

Delay Days <= 0

```



\### 3. Exploratory Data Analysis



The project analyzes:



\* Delivery delay distribution

\* Monthly delivery trends

\* Late-delivery percentages

\* Average delivery time

\* Delivery hotspots

\* Route performance

\* Seller performance

\* Product-category performance

\* Customer-state performance

\* Purchase weekday

\* Seasonal patterns



\### 4. Spike Detection



Monthly delivery performance is analyzed to identify unusual delay spikes.



Months with fewer than 100 orders are excluded from spike analysis to reduce misleading results caused by very small samples.



\### 5. Operational Hotspot Analysis



The dashboard allows users to investigate different dimensions:



\* Route

\* Warehouse proxy (seller state)

\* Seller / fulfilment proxy

\* Product category

\* Customer state

\* Purchase weekday

\* Season



\### 6. High-Delay Combination Analysis



A heatmap is used to analyze delivery delays across:



\*\*Seller State × Customer State\*\*



This helps identify combinations with higher late-delivery percentages.



\---



\## 🤖 Machine Learning



A \*\*Decision Tree Classifier\*\* is included as a baseline delay-risk model.



The model uses information available before delivery, including:



\* Seller state

\* Customer state

\* Product category

\* Purchase weekday

\* Purchase month

\* Number of items

\* Total price

\* Total freight

\* Same-state route



The dashboard reports:



\* Recall for late orders

\* Precision for late orders

\* Overall accuracy

\* Classification report

\* Confusion matrix



Because late-delivery prediction is an imbalanced classification problem, recall and precision for late orders are considered more informative than accuracy alone.



\---



\## 📊 Streamlit Dashboard



The interactive dashboard provides:



\### Delivery Performance Overview



\* Delivered orders

\* On-time percentage

\* Late percentage

\* Average delay of late orders

\* Average delivery time



\### Delay Analysis



\* Delay distribution

\* Monthly delivery trend

\* Unusual delay spikes



\### Operational Hotspots



Interactive analysis by:



\* Route

\* Seller state

\* Seller

\* Product category

\* Customer state

\* Purchase weekday

\* Season



\### Recommendations



The dashboard prioritizes high-delay routes and provides suggested actions such as:



\* Adding delivery-date buffers

\* Reviewing seller handoffs

\* Reviewing transportation plans

\* Monitoring recurring delays



\### Delay-Risk Model



A Decision Tree model can be run directly from the dashboard to evaluate delivery delay risk.



\---



\## 🛠️ Technologies Used



\* Python

\* Pandas

\* Matplotlib

\* Seaborn

\* Scikit-learn

\* Streamlit

\* Jupyter Notebook

\* Google Colab

\* Git

\* GitHub



\---



\## 📁 Project Structure



```text

Delivery-Delay-Operations-Analytics/

│

├── app.py

├── requirements.txt

├── Delivery\_Delay\_Operations\_Analytics.ipynb

├── README.md

└── .gitignore

```



\---



\## 🚀 How to Run the Project



\### Step 1: Install the required libraries



Open PowerShell in the project folder and run:



```bash

python -m pip install -r requirements.txt

```



\### Step 2: Start the Streamlit dashboard



```bash

python -m streamlit run app.py

```



\### Step 3: Open the dashboard



Open the local Streamlit URL shown in the terminal, usually:



```text

http://localhost:8501

```



\### Step 4: Upload the dataset



Upload the five required Olist CSV files through the dashboard sidebar.



\---



\## 📋 Project Files



\### `app.py`



Contains the Streamlit dashboard and data-processing, analysis, visualization, recommendation, and Decision Tree functionality.



\### `requirements.txt`



Contains the Python libraries required to run the dashboard.



\### `Delivery\_Delay\_Operations\_Analytics.ipynb`



Contains the project analysis, data preparation, exploratory analysis, machine learning, findings, and recommendations.



\### `.gitignore`



Prevents CSV datasets, Python cache files, Jupyter checkpoint files, and environment files from being uploaded to GitHub.



\### `README.md`



Provides project documentation and instructions for running the project.



\---



\## ⚠️ Limitations



\* The Olist dataset does not provide actual warehouse identifiers.

\* Carrier information is not available.

\* Detailed delivery-event history is not available.

\* Seller state is therefore used as a warehouse proxy.

\* Seller ID is used as a fulfilment proxy.

\* The Decision Tree is a baseline model and is not intended as a production prediction system.



\---



\## 🔮 Future Improvements



\* Add real carrier information.

\* Add actual warehouse-level data.

\* Integrate real-time delivery-event data.

\* Improve the delay prediction model.

\* Add more advanced machine learning models.

\* Deploy the dashboard online.

\* Add real-time delivery monitoring and alerts.



\---



\## 👨‍💻 Author



\*\*Chetan\*\*





