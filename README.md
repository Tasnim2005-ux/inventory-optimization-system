# 📦 Inventory Optimization & Decision Support System

> **A data-driven inventory analytics and decision-support application for improving stock availability, reducing inventory risk, and supporting smarter replenishment decisions.**

An interactive **Inventory Optimization & Decision Support System** built with Python and Streamlit, designed to transform transactional supply-chain data into actionable inventory insights.

The system integrates **ABC-XYZ inventory classification, demand variability analysis, Safety Stock, Reorder Point (ROP), Economic Order Quantity (EOQ), inventory risk assessment, replenishment analysis, and supplier/warehouse performance evaluation** into a unified analytical platform.

---

## 🎯 Project Overview

Inventory management requires balancing two competing objectives:

- Maintaining sufficient stock to satisfy demand
- Avoiding unnecessary inventory holding and associated costs

Traditional inventory decisions can become difficult when organizations manage multiple **SKUs, warehouses, suppliers, regions, demand patterns, and service-level requirements**.

This project addresses that challenge by developing a centralized analytical system that converts supply-chain data into structured inventory decisions.

### Core Decision Questions

The system is designed to help answer questions such as:

- Which products require the highest inventory attention?
- Which SKUs contribute most significantly to inventory value?
- Which products have stable or highly variable demand?
- How much safety stock should be maintained?
- When should inventory be reordered?
- What order quantity can minimize inventory-related costs?
- Which warehouses present higher inventory risk?
- How are suppliers and warehouses performing?
- What potential impact can inventory optimization have?

---

## 🚀 Key Objectives

1. **Analyze inventory characteristics** across SKUs, warehouses, suppliers, and regions.
2. **Prioritize inventory items** using ABC analysis.
3. **Evaluate demand variability** using XYZ classification.
4. **Determine appropriate safety stock levels** based on demand uncertainty and service levels.
5. **Calculate Reorder Points (ROP)** to support replenishment decisions.
6. **Estimate Economic Order Quantity (EOQ)** for cost-efficient ordering.
7. **Identify inventory risks and potential inefficiencies.**
8. **Evaluate supplier and warehouse performance.**
9. **Provide an interactive decision-support environment** for supply-chain analysis.

---

# 🧠 Analytical Methodology

The system combines multiple inventory-management techniques into a single analytical workflow.

## 1. ABC Analysis

ABC analysis categorizes inventory according to its contribution to cumulative inventory value.

| Class | Cumulative Contribution | Management Priority |
|-------|-------------------------|---------------------|
| **A** | Up to 80% | 🔴 High |
| **B** | 80%–95% | 🟡 Medium |
| **C** | Above 95% | 🟢 Lower |

This allows managers to focus attention and control effort on the inventory items that have the greatest financial impact.

---

## 2. XYZ Analysis

XYZ classification evaluates demand variability.

| Class | Demand Variability | Interpretation |
|-------|-------------------|----------------|
| **X** | CV ≤ 0.50 | Relatively stable demand |
| **Y** | 0.50 < CV ≤ 1.00 | Moderate variability |
| **Z** | CV > 1.00 | Highly variable demand |

Combining ABC and XYZ creates a more informative inventory segmentation framework.

### ABC-XYZ Matrix

Examples include:

- **AX** → High-value, stable-demand items
- **AY** → High-value, moderately variable items
- **AZ** → High-value, highly uncertain items
- **CX** → Low-value, stable-demand items
- **CZ** → Low-value, highly variable items

This helps distinguish between **financial importance** and **demand uncertainty**.

---

# 🛡️ Safety Stock Analysis

Safety stock is used to protect against uncertainty in demand and supply.

The system allows inventory decisions to be evaluated under different target service levels:

- 90%
- 95%
- 97.5%
- 99%

Higher service levels provide greater protection against stockouts but may require additional inventory investment.

The system calculates demand-related measures including:

- Average Daily Demand
- Demand Standard Deviation
- Demand Coefficient of Variation
- Lead-Time Demand
- Safety Stock

---

# 🔄 Reorder Point (ROP)

The Reorder Point determines when inventory should be replenished.

The analytical framework considers:

**Lead-Time Demand + Safety Stock**

This provides a practical mechanism for translating demand uncertainty into a replenishment trigger.

---

# 📦 Economic Order Quantity (EOQ)

EOQ is used to determine an economically efficient order quantity by balancing ordering and holding costs.

The system includes an **EOQ & Cost Optimization** module to support ordering decisions and evaluate inventory-related cost trade-offs.

---

# ⚠️ Inventory Risk Analysis

Inventory risk analysis identifies products and operational areas that may require additional managerial attention.

The system considers indicators such as:

- Demand variability
- Inventory coverage
- Inventory value
- Forecast error
- Stock-related exposure
- SKU-level characteristics

This supports proactive identification of potentially vulnerable inventory segments.

---

# 🚚 Replenishment Analysis

The replenishment module provides a decision-oriented view of inventory requirements.

It helps evaluate:

- Current demand characteristics
- Lead-time demand
- Safety stock requirements
- Reorder thresholds
- Potential replenishment needs

The objective is to move inventory management from **reactive stock monitoring** toward **structured replenishment decisions**.

---

# 🏭 Supplier Performance

Supplier-level analysis provides insights into supply-chain performance across different suppliers.

The system can be used to investigate:

- Supplier-level inventory contribution
- Demand/supply-related patterns
- Performance differences
- Potential supplier-related risk areas

This creates a foundation for supplier-focused inventory decisions.

---

# 🏢 Warehouse Performance

Warehouse-level analysis evaluates inventory behavior across different warehouse locations.

It enables comparison of:

- Inventory levels
- Inventory value
- Demand patterns
- Coverage
- Risk indicators
- Operational differences

This can support warehouse-level planning and resource allocation.

---

# 📊 Optimization Impact

The system includes an **Optimization Impact** module designed to evaluate the potential implications of inventory optimization.

The goal is not simply to display inventory statistics, but to connect analytical results with potential **business and operational improvements**.

---

# 🖥️ Application Modules

| Module | Purpose |
|--------|---------|
| 🏠 Home | System introduction and navigation |
| 📊 Executive Dashboard | High-level inventory KPIs |
| 🔍 Data Overview | Dataset exploration and profiling |
| 📦 ABC-XYZ Analysis | Inventory segmentation |
| 🛡️ Safety Stock & ROP | Stock protection and reorder analysis |
| 🔄 Replenishment | Replenishment decision support |
| 💰 EOQ & Cost Optimization | Order quantity and cost analysis |
| ⚠️ Inventory Risk | Risk identification |
| 🚚 Supplier Performance | Supplier-level analysis |
| 🏭 Warehouse Performance | Warehouse-level analysis |
| 📈 Optimization Impact | Potential optimization impact |

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │   Supply Chain Data  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Data Loading &    │
                    │    Preprocessing     │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │     Inventory Feature Engine    │
              │                                 │
              │ • Demand Metrics                │
              │ • Inventory Value               │
              │ • Forecast Error                │
              │ • Demand Variability            │
              │ • Lead-Time Demand              │
              └────────────────┬────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ABC Analysis      XYZ Analysis     Risk Analysis
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                 ┌──────────────────────────┐
                 │ Inventory Optimization   │
                 │                          │
                 │ • Safety Stock           │
                 │ • ROP                    │
                 │ • EOQ                    │
                 │ • Replenishment          │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Decision Support Layer   │
                 │                          │
                 │ Supplier Performance     │
                 │ Warehouse Performance    │
                 │ Optimization Impact      │
                 └──────────────────────────┘
```

---

# 📁 Project Structure

```text
Inventory-Optimization-Decision-Support-System/
│
├── code/
│   ├── app.py
│   ├── data_loader.py
│   ├── inventory_moduls.py
│   │
│   └── pages/
│       ├── home.py
│       ├── executive_dashboard.py
│       ├── data_overview.py
│       ├── abc_xyz_analysis.py
│       ├── safety_stock_rop.py
│       ├── replenishment.py
│       ├── eoq_cost_optimization.py
│       ├── inventory_risk.py
│       ├── supplier_performance.py
│       ├── warehouse_performance.py
│       └── optimization_impact.py
│
├── data/
│   └── supply_chain_dataset1.csv
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

### Programming & Analytics
- **Python**
- **Pandas**
- **NumPy**

### Application
- **Streamlit**

### Analytical Techniques
- ABC Inventory Classification
- XYZ Demand Classification
- Demand Variability Analysis
- Safety Stock Analysis
- Reorder Point Analysis
- EOQ
- Inventory Risk Analysis
- Supplier & Warehouse Performance Analysis

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Tasnim2005-ux/inventory-optimization-system.git
cd inventory-optimization-system
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Application

```bash
streamlit run code/app.py
```

---

# 📊 Dataset

The project uses a **High-Dimensional Supply Chain Inventory Dataset** containing supply-chain and inventory-related records.

The dataset supports analysis across dimensions such as:

- SKU
- Warehouse
- Supplier
- Region
- Date
- Demand
- Inventory
- Lead Time
- Cost-related variables

The dataset is used to demonstrate how operational data can be transformed into inventory-management insights and decision-support outputs.

---

# 🎓 Academic & Industrial Relevance

This project demonstrates the practical application of **Industrial Engineering, Supply Chain Management, Operations Research, and Data Analytics** concepts.

### Academic Relevance

The project connects theoretical concepts with computational implementation, including:

- Inventory Management
- Operations Research
- Supply Chain Analytics
- Statistical Demand Analysis
- Decision Support Systems
- Optimization Concepts

### Industrial Relevance

A similar analytical framework can support organizations in:

- Inventory planning
- Stock prioritization
- Replenishment planning
- Service-level management
- Warehouse analysis
- Supplier evaluation
- Inventory risk management
- Cost-conscious ordering decisions

---

# 💡 Why This Project Matters

The purpose of the system is not simply to build another dashboard.

It demonstrates a progression from:

```text
Raw Operational Data
        ↓
Data Processing
        ↓
Analytical Metrics
        ↓
Inventory Classification
        ↓
Optimization Models
        ↓
Risk & Performance Analysis
        ↓
Decision Support
```

The central idea is to transform **data into decisions**.

---

# 🚀 Future Development

Potential extensions include:

- 📈 Machine Learning-based demand forecasting
- 🔮 Probabilistic demand modeling
- 🎯 Multi-echelon inventory optimization
- 🚚 Transportation-aware replenishment
- 🏭 Multi-warehouse inventory allocation
- 🔗 Supplier lead-time uncertainty modeling
- 📉 Advanced inventory cost optimization
- 🤖 Automated replenishment recommendations
- 🧮 Linear / Mixed-Integer Optimization
- 📊 Scenario-based inventory simulation
- 🌐 Digital Supply Chain Decision Support System

These extensions can move the project toward a more comprehensive **Operations Research and Supply Chain Optimization framework**.

---

# 📌 Current Status

**Project Status:** Completed Prototype / Decision-Support Application

The system currently integrates multiple inventory analytics and optimization-oriented modules into an interactive Streamlit application.

---

# 👤 Author

**Tasnim Bin Nasim**  
Industrial & Production Engineering  
Jashore University of Science and Technology (JUST), Bangladesh

### Areas of Interest

- Supply Chain Analytics
- Operations Research
- Inventory Optimization
- Operations Management
- Business Analytics
- Data-Driven Decision Making

---

# ⭐ Project Philosophy

> **“The goal is not only to understand what happened — but to determine what should happen next.”**
