**Risk Wise: A Terms of Service Assessor & Analyser** 

**1\. Abstract** 

**1.1 Executive Summary Points** 

● **Problem:** Information asymmetry in "clickwrap" agreements exposes users to hidden risks. 

● **Gap:** Manual legal review is costly; standard AI lacks structural reasoning. ● **Solution:** A Hybrid RAG framework integrating Knowledge Graphs with Vector Search. ● **Method:** LLM-driven triple extraction grounds semantic retrieval in structured logic. ● **Impact:** Democratized, hallucination-free legal risk assessment for the layperson. 

**1.2 Extended Abstract** 

The digital economy operates on a foundation of contractual ubiquity, where the exchange of data and services is governed by Terms of Service (ToS) agreements. These documents, universally accepted yet rarely comprehended, represent a critical failure of informed consent. "Risk Wise" proposes a novel, algorithmic solution to this crisis of understanding, designed as a final year university project that pushes the boundaries of current Legal Artificial Intelligence (LegalAI). 

The core premise of this research is that the complexity of legal text cannot be solved by "flat" statistical analysis alone. Traditional Natural Language Processing (NLP) and even modern Large Language Models (LLMs) often fail to capture the binding, hierarchical, and cross-referential nature of legal contracts. Standard Retrieval-Augmented Generation (RAG) systems, which rely on vector similarity, suffer from context fragmentation—retrieving isolated clauses while missing the vital definitions or exceptions located elsewhere in the document. This leads to "hallucinations," where an AI might confidently misinterpret a user's liability or rights. Risk Wise introduces a **Hybrid Architecture** that fuses the semantic flexibility of Vector Databases with the deterministic structure of Knowledge Graphs (KGs). By embedding document chunks for similarity search while simultaneously constructing a persistent graph of legal entities and relationships via LLM-driven triple generation, the system creates a "Risk Graph." This graph captures the logical flow of the contract (e.g., (Provider)--\>(Service) subject to (Condition)). When a user queries the system, the retrieval logic leverages this graph to traverse semantic connections that vector search misses, retrieving a rich, structurally sound context for the generative model. 

This report details the architectural design, theoretical validation through a comprehensive literature survey, and the implementation strategy using a microservices stack (Neo4j, LangChain, Docker). By addressing the research gaps identified in recent studies—specifically the lack of structural awareness in open-source LLMs and the need for explainable unfairness detection—Risk Wise aims to provide a robust, audit-capable tool that empowers users to identify predatory clauses, bridging the gap between legal jargon and human understanding.  
**2\. Problem Statement** 

**2.1 The Crisis of Uninformed Consent** 

The modern consumer interaction with digital services is characterized by a fundamental paradox: the "clickwrap" agreement. Users are required to legally bind themselves to Terms of Service (ToS) agreements to access basic utilities, social networks, and financial tools. However, these documents are deliberately engineered to be inscrutable. They are characterized by extreme length, dense "legalese," and recursive syntax that obscures the true nature of the exchange. 

The problem is not merely inconvenience; it is a systemic **information asymmetry**. Service providers employ sophisticated legal teams to draft agreements that maximize corporate protection and data exploitation rights (e.g., forced arbitration, unilateral modification, expansive data licensing), knowing that the friction of reading these documents ensures they remain unread. The average user lacks both the time and the specialized legal knowledge to decipher the implications of clauses like "indemnification" or "waiver of class action." Consequently, millions of users unknowingly consent to unfair terms that compromise their privacy, intellectual property rights, and legal recourse. Current solutions are insufficient: manual legal review is prohibitively expensive, and existing automated tools (like keyword search or basic summarizers) lack the nuance to identify "dark patterns" or interpret complex, multi-hop legal logic. There is an urgent need for an automated, intelligent system capable of parsing these documents with the rigor of a lawyer but the accessibility of a consumer app—a system that makes the "fine print" visible and understandable. 

**2.2 The Limitations of Current AI in Law** 

While Generative AI has shown promise, its application to law is fraught with risk. "Hallucination"—the fabrication of facts—is unacceptable in legal analysis. A standard LLM might invent a clause that doesn't exist or misinterpret the relationship between two conflicting sections (e.g., a "Privacy Promise" in Section 1 and a "Data Sale" right in Section 15). Furthermore, traditional RAG systems treat documents as unstructured "bags of words," losing the vital hierarchical context (Titles, Articles, Clauses) that defines legal meaning. This lack of "structural awareness" renders standard AI tools unreliable for high-stakes risk assessment. 

**3\. Objectives** 

The "Risk Wise" project aims to bridge the gap between complex legal texts and consumer understanding through the following salient objectives: 

1\. **Develop a Hybrid Retrieval Framework:** To engineer a system that combines **Vector Similarity Search** (for fuzzy semantic matching) with **Knowledge Graph Traversal** (for structured, relational reasoning). This objective addresses the limitation of "flat" retrieval by ensuring the system can follow the logical threads of a contract (e.g., linking a definition to its usage across the document). 

2\. **Automate Structural Knowledge Extraction:** To implement a pipeline that utilizes an LLM to automatically parse unstructured legal text into **Subject-Predicate-Object triples**. This creates a persistent Knowledge Graph that maps the entities (Provider, User, Content) and their normative relationships (Obligation, Permission, Prohibition),  
preserving the document's logical hierarchy. 

3\. **Enable Explainable "Unfairness" Detection:** To move beyond simple summarization by specifically training or prompting the system to detect and flag **unfair contractual terms** (e.g., "Dark Clauses" such as non-consensual data sharing or liability waivers). The objective is to provide the user with a "Risk Score" and a plain-language explanation of *why* a clause is dangerous, citing the specific source text. 

4\. **Mitigate Hallucination via Graph Grounding:** To enhance the reliability of legal advice by constraining the LLM's generation to facts explicitly retrieved from the Knowledge Graph. By requiring the system to cite the specific node and edge relationships that inform its answer, the project aims to create a **verifiable audit trail** for every claim it makes. 

5\. **Democratize Legal Access:** To deploy this complex backend via a **user-friendly web interface** that allows laypeople to upload PDFs and receive instant, expert-level analysis. This objective focuses on usability, ensuring that the output is not just accurate but actionable for a non-expert audience. 

**4\. Literature Review** 

The development of "Risk Wise" is situated at the intersection of Legal Informatics, Graph Representation Learning, and Retrieval-Augmented Generation (RAG). To validate our methodology and identify the specific research gaps our project fills, we conducted a survey of recent, high-impact papers from 2024 and 2025\. 

**4.1 Comparative Analysis Table** 

The following table summarizes four pivotal research papers, identifying their core contributions, their limitations (research gaps), and how the "Risk Wise" framework improves upon them.

| Paper Title &  Reference | Core Methodology  | Research Gaps  Identified | Improvement in "Risk Wise" |
| :---- | ----- | :---- | ----- |
| **SAT-Graph RAG: Structure-Aware  Temporal Graph RAG for Legal Norms  Text to Trust:  Evaluating... Models for Unfair Terms of Service Detection** | Proposes an  ontology-driven graph RAG that models the **hierarchical and  temporal** structure of legislation (e.g.,  Constitutions). Uses "Work" vs. "Expression"nodes to track  amendments over time. A systematic  benchmark of LLMs (BERT, Llama, SaulLM)for **classifying** clauses as "fair" or "unfair" | **Scope Limitation:** Focuses heavily on *public law* (legislation) and *temporal evolution* (amendments). It does not address the  adversarial nature of *private contracts* (ToS) or the detection of "unfair clauses." The    temporal complexity is unnecessary for static ToS uploads.  **Lack of Explainability:**Focuses on binary *classification* (Labeling)    rather than *explanation*.It tells you a clause is | **Domain Adaptation:** Adapts the structural graph approach to **private law**. Instead of temporal versioning, Risk Wise focuses on **normative logic**  (identifying loops and traps in static text) and specifically targets **unfairness detection**, which SAT-Graph  ignores.  **RAG Integration:**    Moves beyond  classification to  **reasoning**. Risk Wise    uses the KG to *retrieve* |

| Paper Title &  Reference | Core Methodology  | Research Gaps  Identified | Improvement in "Risk Wise" |
| :---- | :---- | :---- | :---- |
|  | using the CLAUDETTE dataset. Compares Fine-Tuning vs. LoRA vs. Zero-shot. | bad but not *why* or howit relates to other  clauses. **No Retrieval:** It analyzes clauses in isolation, missing  cross-referential risks. | the context of an unfair clause (e.g., its  definition) and uses the LLM to **generate a natural language explanation** of the risk,bridging the gap  between detection and user understanding. |
| **ContractEval: A  Benchmark for  Evaluating LLMs on Contract Review** | Benchmarks  open-source vs.  proprietary LLMs on contract clause  extraction (CUAD dataset). Finds that open-source models suffer from **"laziness"** (failing to retrieve  existing clauses) and lack accuracy. | **Retrieval Failure:** Highlights that even large context windows fail to capture complex dependencies in long contracts. Shows that relying solely on LLMs without structured retrieval leads to poor recall ("laziness"). | **Structural Forcing:** Addresses "laziness" by using the  **Knowledge Graph** to *force* the retrieval of connected nodes. Evenif the LLM is "lazy," the graph traversal  mechanically surfaces the relevant hidden clauses, improving performance on  open-source models. |
| **Hybrid Graph RAG: Harnessing Graph and Vector for  Financial Analysis** | Demonstrates a  practical **Hybrid RAG** pipeline (Neo4j \+  LangChain) for financialreports. Combines vector search (fuzzy) with graph search (entity linking) for  multi-hop reasoning. | **Domain Specificity:** Tailored for *quantitative* data (financial entities, revenue, dates). Lacks the **legal ontology** required to understand *normative* relationships (Obligation,  Permission, Prohibition)found in text-heavy legal documents. | **Legal Schema  Design:** Adopts the Hybrid Architecture but replaces the financial schema with a **Legal Risk Schema**  (Provider, User,  Liability, Termination). Focuses on **deontic logic** rather than  financial metrics,  optimizing the graph forqualitative legal  reasoning. |

 

 

**4.2 Narrative Synthesis** 

**4.2.1 The Structural Deficit in Standard RAG** 

The foundational premise of our literature review is that standard RAG is insufficient for law. The paper on **SAT-Graph RAG** provides the strongest theoretical argument for this. It posits that legal documents are not merely text; they are "structured programs" composed of hierarchical elements (Articles, Chapters) and temporal versions. Standard RAG, which relies on "flat" text chunking and vector similarity, is "blind" to this structure. For example, a vector search might  
retrieve a clause about "Termination" but miss the "Definitions" section that defines "Termination" in a highly restrictive way, simply because the definition text doesn't share keywords with the user's query. 

"Risk Wise" adopts the *structural awareness* advocated by SAT-Graph but pivots the application. While SAT-Graph focuses on the *temporal* evolution of laws (how Article 5 changed from 1988 to 1999\) , our project focuses on the *relational* logic of static contracts. We argue that for a ToS Analyzer, the "time" dimension is less critical than the "cross-reference" dimension. Our Knowledge Graph is designed to map the internal citations (e.g., "subject to Section 4.2") that create legal traps. 

**4.2.2 The Gap Between Detection and Comprehension** 

The **Text to Trust** paper represents the state-of-the-art in *detecting* unfair clauses. By fine-tuning models like BERT on the CLAUDETTE dataset, the authors achieved high accuracy in flagging problematic text. However, their approach is limited to *classification*. A label of "Unfair" is useful for a regulator, but a user needs an *explanation*. Furthermore, the paper notes that general-purpose LLMs often misclassify due to "limited domain grounding". "Risk Wise" addresses this gap by integrating the detection capability into a **Generative RAG** pipeline. We don't just classify a clause; we use the Knowledge Graph to retrieve the *context* of that clause and then ask the LLM to explain the unfairness. This moves the system from a "Black Box" classifier to an "Explainable AI" (XAI) agent. 

**4.2.3 Solving the "Laziness" of LLMs** 

The **ContractEval** benchmark reveals a critical weakness in current LLMs: "laziness." When presented with long contracts, models often fail to extract relevant clauses, returning "no related clause" even when one exists. This is a failure of *attention*. The model gets lost in the noise of the document. 

This finding validates our **Hybrid Architecture**. By using a Knowledge Graph, we introduce a deterministic retrieval mechanism. If a user asks about "Liability," we don't rely on the LLM to "read" the whole document. We traverse the graph from the "Liability" node to all connected nodes. This "structural forcing" ensures that the relevant clauses are fed into the LLM's context window, effectively curing the "laziness" identified in ContractEval. 

**4.2.4 The Necessity of Hybrid Retrieval** 

Finally, the literature on **Hybrid Graph RAG** confirms that neither Vector Search nor Graph Search is sufficient alone. Vector search is robust for fuzzy queries (handling synonyms like "cancel" vs "terminate"), while Graph search is superior for multi-hop reasoning (connecting "Provider" to "Data" to "Third Party"). The "Risk Wise" architecture explicitly implements this hybridity, using **Reciprocal Rank Fusion** (as suggested in ) to combine the results of both 

retrieval methods. This ensures that our system captures both the *spirit* (semantic) and the *letter* (structural) of the law. 

**5\. Methodology & Architecture** 

The "Risk Wise" framework employs a sophisticated multi-stage pipeline designed to transform  
unstructured PDF documents into a queryable, structured knowledge base. The architecture is built on the principle of **"Graph-Enhanced RAG,"** where the Knowledge Graph serves as the "brain" that guides the retrieval process of the vector "memory." 

**5.1 System Architecture Overview** 

The system is composed of five distinct, interconnected modules: 

1\. **Ingestion & Semantic Chunking:** Intelligent parsing of legal documents. 2\. **Vector Embedding:** Creation of a dense vector index for similarity search. 3\. **Knowledge Graph Construction:** LLM-driven extraction of entities and triples. 4\. **Hybrid Retrieval Engine:** A unified query processor merging Vector and Graph signals. 5\. **Generative Reasoning:** Context-aware response generation with citation. 

**5.2 Detailed Methodological Steps** 

**5.2.1 Document Ingestion and Semantic Parsing** 

The process begins with the user uploading a Terms of Service document (PDF). ● **Text Extraction:** We utilize **unstructured.io** or **PyPDF** to extract text. Crucially, this step involves **layout analysis** to identify headers, footers, and section numbers. ● **Semantic Chunking:** Unlike naive chunking (splitting every 500 characters), we employ **"Parent-Child" chunking**. The document is split into small "Child" chunks (individual clauses) that are linked to larger "Parent" chunks (whole sections). This preserves the context. If a clause says "Not applicable," the Parent chunk tells us *what* is not applicable. ○ *Implementation:* Each chunk is assigned a unique ID and tagged with metadata (Section Number, Page Number). 

**5.2.2 Vectorization and Indexing** 

● **Embedding Model:** The text chunks are passed through an embedding model. We utilize **OpenAI's text-embedding-3-small** or a high-performance open-source model like **all-MiniLM-L6-v2**. These models map the semantic meaning of the text into a high-dimensional vector space. 

● **Vector Database:** These vectors are stored in a **Vector Store** (e.g., **ChromaDB** or **Neo4j's Vector Index**). This allows for KNN (K-Nearest Neighbor) search. ○ *Function:* This component handles "fuzzy" queries. If a user asks "Can they kick me off?", the vector store matches this to clauses containing "termination," 

"suspension," or "ban," even if the exact keywords differ. 

**5.2.3 Knowledge Graph Construction (Triple Generation)** 

This is the core innovation of "Risk Wise." Parallel to vectorization, the system builds a structured graph. 

● **Triple Extraction LLM:** We employ a "Triple Generating LLM" (e.g., **GPT-4** or a fine-tuned **Llama 3**) with a specialized prompt. This prompt instructs the model to read each text chunk and extract logical relationships in the form of (Subject, Predicate, Object) triples. 

○ *Example:* For the text "We may share your personal data with third-party  
advertisers," the LLM generates: 

■ (:Provider)--\>(:User\_Data) 

■ (:User\_Data)--\>(:Advertisers) 

● **Ontology Mapping:** The extracted entities are mapped to a predefined **Legal Ontology** (e.g., Entities: Provider, User, Content, Liability; Relationships: OBLIGATED\_TO, PERMITTED\_TO, PROHIBITED\_FROM). This ensures consistency. 

● **Graph Storage:** These triples are stored in **Neo4j**, a graph database. Crucially, each node is linked back to the *original text chunk ID* in the Vector DB. This creates a "Graph of Chunks," anchoring the abstract logic to the concrete text. 

**5.2.4 Hybrid Retrieval Logic** 

When a user submits a natural language query (e.g., "What happens to my photos if I delete my account?"): 

1\. **Vector Search:** The system converts the query into a vector and retrieves the top-K most similar text chunks from the Vector DB. 

2\. **Graph Traversal:** The system identifies the entities in the query ("Photos", "Delete", "Account") and locates the corresponding nodes in the Knowledge Graph. It then performs a **multi-hop traversal** (e.g., 2 hops) to find related concepts. 

○ *Logic:* It finds the Content node (synonym for "Photos"), follows the RETAINED\_BY edge, and finds a node License. It retrieves the chunks associated with this License node. 

3\. **Result Fusion:** The system combines the chunks retrieved from Vector Search and Graph Traversal. This captures both the *explicit* answer (found by vector) and the *implicit* context (found by graph). 

**5.2.5 Generative Analysis and Audit Trails** 

● **Persistent Prompting:** The aggregated context is fed into the final **Reasoning LLM**. The prompt is optimized to act as a "Legal Risk Assessor." 

● **Instruction:** "You are an expert lawyer. Using *only* the provided context, answer the user's question. You must cite the specific Section ID for every claim. Identify any clauses that fit the definition of 'Unfair Contract Terms'." 

● **Output:** The system generates a natural language response with inline citations (e.g., "The provider retains a perpetual license to your photos (Section 4.2), even after account termination (Section 9.1)"). This citation mechanism creates the **Audit Trail** required for trust. 

**6\. Hardware and Software Requirements** 

To successfully implement the "Risk Wise" architecture, a robust and scalable technology stack is required. The system is designed as a containerized microservices application to ensure modularity and ease of deployment. 

**6.1 Software Requirements**

| Component  | Technology / Tool  | Purpose & Justification |
| :---- | :---- | :---- |
| **Orchestration**  | **Docker & Docker Compose**  | Manages the lifecycle of the various services (API,  Database, Frontend) ensuring environmental consistency. |
| **Graph Database**  | **Neo4j**  | The industry-standard Graph DB. Supports the **Cypher** querylanguage for complex  traversals and includes native Vector Indexing capabilities for hybrid search. |
| **Vector Database**  | **ChromaDB** or **Pinecone**  | (Optional if not using Neo4j Vector) Specialized storage for high-dimensional embeddings. ChromaDB is preferred for localdevelopment. |
| **LLM Orchestration**  | **LangChain** or **LlamaIndex**  | The "glue" code. specialized libraries for chaining prompts, managing retrieval logic, and handling context windows. |
| **Backend Framework**  | **FastAPI (Python)**  | High-performance,  asynchronous web framework. Ideal for handling concurrent API requests and long-running inference tasks. |
| **Frontend**  | **React.js** or **Vue.js**  | Provides a responsive, clean interface for document upload and visualization. React's component ecosystem aids in rendering complex data like graphs. |
| **LLM Provider**  | **OpenAI API (GPT-4o)**  | Primary model for Triple Extraction and Reasoning due to superior instruction-following. |
| **Alternative LLM**  | **Ollama (Llama 3\)**  | For **local/private** deployment. Essential for law firms or users concerned with data privacy. |
| **Parsing**  | **Unstructured.io**  | Advanced PDF parsing to handle multi-column layouts and tables common in legal docs. |

 

 

**6.2 Hardware Requirements** 

The hardware needs vary based on the deployment strategy (Cloud API vs. Local Inference). ● **Standard Deployment (Cloud API-based):** 

○ **CPU:** Modern Multi-core Processor (e.g., Intel Core i7 or AWS **t3.xlarge**) to handle parsing and API routing.  
○ **RAM: 16 GB** minimum. (Neo4j requires significant heap memory for efficient graph traversal). 

○ **Storage: 50 GB SSD**. Graph databases can grow quickly; fast I/O is critical for retrieval performance. 

○ **Network:** High-bandwidth connection for API calls to OpenAI/Pinecone. ● **Privacy-First Deployment (Local LLM):** 

○ *If running the Triple Generation or Reasoning models locally (e.g., Llama 3 8B):* ○ **GPU: NVIDIA GPU** with at least **16 GB VRAM** (e.g., RTX 4080 or A10G). This is non-negotiable for acceptable inference latency. 

○ **RAM: 32 GB** System RAM (to hold the vector index and model weights in memory). ○ **Cooling:** Adequate thermal management for sustained inference loads. 

**7\. References** 

H. de Martim, "An Ontology-Driven Graph RAG for Legal Norms: A Structural, Temporal, and Deterministic Approach," *arXiv preprint arXiv:2505.00039*, 2025\. 

N. P. P. Juttu, S. Singireddy, S. Gona, and S. Timilsina, "Text to Trust: Evaluating Fine-Tuning and LoRA Trade-offs in Language Models for Unfair Terms of Service Detection," *arXiv preprint arXiv:2510.22531*, 2025\. 

Z. Wang et al., "ContractEval: A Benchmark for Evaluating LLMs on Contract Review," *arXiv preprint arXiv:2508.03080*, 2025\. 

A. Jha, A. Salinas, and F. Morstatter, "Knowledge Graph Analysis of Legal Understanding and Violations in LLMs," *arXiv preprint arXiv:2511.08593*, 2025\. 

"Hybrid Graph RAG: Harnessing Graph and Vector for Financial Analysis," *Towards AI*, 2024\. "Risk Wise: A Terms of Service Assessor & Analyser Project Proposal," University Project Documentation, 2025\. 

"Advanced RAG Techniques: GraphRAG and Hybrid Retrieval," *Neo4j Blog*, 2025\. "The Rise of Accountable AI Agents: How Knowledge Graphs Solve the Autonomy Problem," *Data Science Central*, 2025\. 

"RAG with Knowledge Graphs for legal documents," *arXiv preprint arXiv:2505.00039v3*, 2025\. *Note: This report synthesizes findings from the provided research snippets to construct a comprehensive academic analysis suitable for a final year university project. The methodology and architecture described are derived from the project proposal and enhanced by state-of-the-art techniques found in the referenced literature.* 

**Works cited** 

1\. Deterministic Legal Retrieval: An Action API for Querying the SAT-Graph RAG \- arXiv, https://arxiv.org/html/2510.06002v1 2\. How knowledge graphs take RAG beyond retrieval \- QED42, https://www.qed42.com/insights/how-knowledge-graphs-take-rag-beyond-retrieval 3\. Leveraging Knowledge Graphs and LLMs for AI Research Idea Generation \- arXiv, https://arxiv.org/html/2503.08549v1 4\. Automating Knowledge Graphs with LLM Outputs | Prompts.ai, https://www.prompts.ai/en/blog/automating-knowledge-graphs-with-llm-outputs 5\. Text to Trust: Evaluating Fine-Tuning and LoRA Trade-offs in Language Models for Unfair Terms of Service Detection \- arXiv, https://arxiv.org/html/2510.22531v1 6\. Predicting potentially unfair clauses in Chilean terms of services with natural language processing \- arXiv, https://arxiv.org/html/2502.00865v1 7\. SafeRBench: A Comprehensive Benchmark for Safety  
Assessment in Large Reasoning Models \- arXiv, https://arxiv.org/html/2511.15169v1 8\. \[2505.00039\] An Ontology-Driven Graph RAG for Legal Norms: A Structural, Temporal, and Deterministic Approach \- arXiv, https://arxiv.org/abs/2505.00039 9\. Graph RAG for Legal Norms: A Hierarchical, Temporal and Deterministic Approach \- arXiv, 

https://arxiv.org/html/2505.00039v3 10\. Text to Trust: Evaluating Fine-Tuning and LoRA Trade-offs in Language Models for Unfair Terms of Service Detection \- ResearchGate, https://www.researchgate.net/publication/396967017\_Text\_to\_Trust\_Evaluating\_Fine-Tuning\_an d\_LoRA\_Trade-offs\_in\_Language\_Models\_for\_Unfair\_Terms\_of\_Service\_Detection 11\. ContractEval: Benchmarking LLMs for Clause-Level Legal Risk Identification in Commercial Contracts \- arXiv, https://arxiv.org/html/2508.03080v1 12\. Hybrid Graph RAG: Harnessing Graph and Vector Databases for Advanced 10-K Insights, 

https://pub.towardsai.net/hybrid-graph-rag-harnessing-graph-and-vector-for-financial-analysis-7 2c3a9f1a09d 13\. Advanced RAG Techniques for High-Performance LLM Applications \- Graph Database & Analytics \- Neo4j, https://neo4j.com/blog/genai/advanced-rag-techniques/ 14\. Knowledge Graph LLM \- TigerGraph, 

https://www.tigergraph.com/glossary/knowledge-graph-llm/ 15\. An Ontology-Driven Graph RAG for Legal Norms: A Structural, Temporal, and Deterministic Approach \- arXiv, https://arxiv.org/html/2505.00039v5 16\. Knowledge Graph Analysis of Legal Understanding and Violations in LLMs \- arXiv, https://arxiv.org/html/2511.08593v1 17\. Knowledge Graph Analysis of Legal Understanding and Violations in LLMs \- ResearchGate, 

https://www.researchgate.net/publication/397556326\_Knowledge\_Graph\_Analysis\_of\_Legal\_U nderstanding\_and\_Violations\_in\_LLMs 18\. The rise of accountable AI agents: How knowledge graphs solve the autonomy problem, 

https://www.datasciencecentral.com/the-rise-of-accountable-ai-agents-how-knowledge-graphs-s olve-the-autonomy-problem/