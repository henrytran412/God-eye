2026 IEEE 50th Annual Computers, Software, and Applications Conference (COMPSAC)
| Provenance-Aware |           |     |     |     | Trust      | Framework |             |     | for | Autonomous |        |     |     |
| ---------------- | --------- | --- | --- | --- | ---------- | --------- | ----------- | --- | --- | ---------- | ------ | --- | --- |
|                  | Vehicles: |     |     | A   | Generative |           | AI-Inspired |     |     |            | Hybrid |     |     |
04400.6202.19096CASPMOC/9011.01 :IOD | EEEI 6202© 00.13$/62/3-7944-5133-8-979 | )CASPMOC( ecnerefnoC snoitacilppA dna ,erawtfoS ,sretupmoC launnA ht05 EEEI 6202
| Approach |     |     | for   | Decentralized    |     |     | Information |     |          |         | Validation |        |     |
| -------- | --- | --- | ----- | ---------------- | --- | --- | ----------- | --- | -------- | ------- | ---------- | ------ | --- |
|          |     |     | N. M. | Istiak Chowdhury |     |     |             |     | Mohammad | Zakaria |            | Haider |     |
Dept. of Computer Science Dept. of Electrical and Computer Engineering
University of Alabama at Birmingham Florida International University
|     |     | Birmingham, |                  | AL      | 35294-1241 |     |     |     | Miami,           | Florida | 33174 |     |     |
| --- | --- | ----------- | ---------------- | ------- | ---------- | --- | --- | --- | ---------------- | ------- | ----- | --- | --- |
|     |     |             | ichowdhu@uab.edu |         |            |     |     |     | mhaid010@fiu.edu |         |       |     |     |
|     |     | Mohammad    |                  | Ashiqur | Rahman     |     |     |     |                  | Ragib   | Hasan |     |     |
Knight Foundation School of Computing and Information Science Dept. of Computer Science
Florida International University University of Alabama at Birmingham
|     |     |     | Miami,           | Florida | 33174 |     |     |     | Birmingham,   | AL  | 35294-1241 |     |     |
| --- | --- | --- | ---------------- | ------- | ----- | --- | --- | --- | ------------- | --- | ---------- | --- | --- |
|     |     |     | marahman@fiu.edu |         |       |     |     |     | ragib@uab.edu |     |            |     |     |
Abstract—Autonomous vehicles (AVs) increasingly rely on trustworthy, and free from malicious tampering. Provenance
information from diverse, decentralized sources, such as peer- offers a foundation for solving this problem, but alone it isn’t
to-peer networks, vehicle-to-vehicle communications, third-party enough in highly decentralized systems where adversaries
applications,andinfrastructureproviders.Whilethisinformation
|     |     |     |     |     |     |     | may forge | or manipulate | data. | Ensuring |     | the authenticity | and |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------- | ----- | -------- | --- | ---------------- | --- |
enablessafernavigation,real-timedecision-making,andsoftware
maintenance,italsointroducescriticalsecuritychallengesrelated trustworthiness of information is crucial for the safety and
to the authenticity and trustworthiness of the data received. trust of AV ecosystems. A single instance of malicious or
Provenance is the ability to trace the origin and history of misleading information, such as false road condition reports,
data, which offers a foundation for addressing these challenges. altered traffic data, or compromised software patches, can
| However,   | in highly | distributed      |     | environments, | cryptographic  |     |                |           |           |     |             |         |          |
| ---------- | --------- | ---------------- | --- | ------------- | -------------- | --- | -------------- | --------- | --------- | --- | ----------- | ------- | -------- |
|            |           |                  |     |               |                |     | lead to severe | outcomes, | including |     | collisions, | traffic | jams, or |
| provenance | alone     | is insufficient, | as  | malicious     | or compromised |     |                |           |           |     |             |         |          |
entities can still propagate misleading or cryptographically valid widespreadexploitationofAVfleets[3].AsAVsbecomemore
yet falsified information. This paper proposes a provenance- integrated into smart transportation systems, gaining public
aware trust framework that combines provenance verification, trustandregulatoryapprovaldependsontheirabilitytooperate
| reputation-based | evaluation, |     | and | behavioral | anomaly | detection |          |                  |     |             |     |         |               |
| ---------------- | ----------- | --- | --- | ---------- | ------- | --------- | -------- | ---------------- | --- | ----------- | --- | ------- | ------------- |
|                  |             |     |     |            |         |           | securely | in decentralized | and | potentially |     | hostile | environments. |
withatwo-stageAI-drivenvalidationagent.Theagentintegrates
Therefore,developingarobustmethodforvalidatingdistributed
| a fine-tuned | transformer-based |     | classifier | for | real-time | behavioral |     |     |     |     |     |     |     |
| ------------ | ----------------- | --- | ---------- | --- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
dataiscrucialtoensuringsafeandreliableautonomousdriving.
| pattern | recognition | with a | structured | contextual | reasoning | layer |     |     |     |     |     |     |     |
| ------- | ----------- | ------ | ---------- | ---------- | --------- | ----- | --- | --- | --- | --- | --- | --- | --- |
for evidence fusion and trust score generation. Together, these AV communication environments are constantly changing
componentsenableAVstoassessthetrustworthinessofincoming
andspanmanyinterconnectedcomponentsorsystems,making
| information  | by jointly | evaluating   | source | provenance,   | behavioral    |     |                |                |     |          |          |             |          |
| ------------ | ---------- | ------------ | ------ | ------------- | ------------- | --- | -------------- | -------------- | --- | -------- | -------- | ----------- | -------- |
|              |            |              |        |               |               |     | them difficult | to manage      | or  | secure.  | Unlike   | centralized | systems  |
| consistency, | and peer   | credibility. |        | Unlike purely | cryptographic |     |                |                |     |          |          |             |          |
|              |            |              |        |               |               |     | with clear     | trust anchors, |     | AVs must | interact | with        | peers of |
approaches,theframeworkdetectssubtleanomaliesandmalicious
intent even from cryptographically legitimate but compromised varyingcredibility,unknownorigins,andinconsistenthistories.
sources. The proposed approach aims to improve accountability Reputation systems can help, but they are often vulnerable
andsafeadoptionofdecentralizedinformation,ultimatelyenhanc- to collusion or Sybil attacks [4]. Similarly, cryptographic
ing the security and trustworthiness of connected autonomous verification of provenance can confirm data origin but cannot
vehicles.
Index Terms—AV; provenance; AI agent; security; trustworthi- ensure that the origin itself is trustworthy [5]. Furthermore,
ness. AVs receive information in multiple formats, such as text
|     |     |                 |     |     |     |     | updates,        | sensor data, | and | alerts, | which | require | fusion and |
| --- | --- | --------------- | --- | --- | --- | --- | --------------- | ------------ | --- | ------- | ----- | ------- | ---------- |
|     |     | I. INTRODUCTION |     |     |     |     | cross-checking. |              |     |         |       |         |            |
Autonomous vehicles (AVs) depend heavily on continuous To address these challenges, we propose a provenance-
datastreamstonavigatesafely,stayoperationallyefficient,and aware trust framework that combines provenance verification,
adjust to changing road conditions [1]. This information can reputation-based assessment, and multi-modal data analysis
come from vehicle-to-vehicle (V2V) communication, peer-to- with an AI–based driving assistant. This frameworkhelps AVs
peer (P2P) exchanges, roadside infrastructure, and third-party evaluate the trustworthiness of incoming data by analyzing its
service providers [2]. However, the distributed and diverse source, cross-referencing peer reputations, and checking for
nature of these sources presents a critical security concern of consistency across different data types. The AI-based model
howanAVcanverifythattheinformationitreceivesisgenuine, serves as an intelligent decision-support system, integrating
| 2836-3795/26/$31.00 ©2026 IEEE |     |     |     |     |     |     | 2923 |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
DOI 10.1109/COMPSAC69091.2026.00440
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.

diverse signals, detecting behavioral inconsistencies, and continuous flow of information exchanged among vehicles,
generating calibrated trust scores to determine whether to roadside units, cloud services, and third-party applications [8].
accept, quarantine, or reject incoming information. This interaction is essential because no single vehicle can
While prior work has combined AI and cryptographic independently perceive or understand the entire environment.
approaches for vehicular security [3], we propose a two-stage Traffic alerts from nearby cars, road condition updates from
discriminative-generative pipeline with a formally specified local sensors, and software patches from different vendors all
selective abstention mechanism calibrated to AV latency contribute to safer and more efficient driving [9]. However,
constraints, providing a concrete architecture that resolves this dependence on external information also makes AVs
the ambiguity in prior work between generative reasoning vulnerable to misinformation, tampered updates, or malicious
as a concept and a deployable implementation. We also data injections. As vehicles become increasingly connected,
present a quantitative analysis of safety trade-off in hy- the challenge is not only in receiving information but also in
brid AI-cryptographic AV trust systems, providing a risk- recognizing which information to trust.
acceptance rationale and a tiered policy recommendation Traditional cryptographic mechanisms such as digital signa-
that can directly inform automotive safety case development tures,hashfunctions,andpublickeyinfrastructures(PKI)have
under ISO 26262 [6] and ISO/SAE 21434 [7]. Together, longbeenemployedtoensuredataconfidentiality,integrity,and
these contributions move the field from proof-of-concept authenticationinconnectedsystems[10].InthecontextofAVs,
demonstrations toward operationally grounded system design. these techniques are used to secure communication channels,
Contribution: Our work bridges the gap between conceptual verify software updates, and prevent unauthorized data manip-
AI reasoning and deployable vehicular security by addressing ulation [3]. While cryptography can confirm the origin and
three critical bottlenecks in autonomous trust frameworks: integrityofamessage,itdoesnotinherentlyverifythesender’s
|       |         |              |              |     |      |              | trustworthiness |     | or intent. | For example, | a   | malicious | vehicle |
| ----- | ------- | ------------ | ------------ | --- | ---- | ------------ | --------------- | --- | ---------- | ------------ | --- | --------- | ------- |
| 1) We | propose | a dual-stage | architecture |     | that | resolves the |                 |     |            |              |     |           |         |
conflict between reasoning and real-time. By combining or compromised infrastructure node could still send false
a high-speed DistilBERT-based classifier with a struc- yet cryptographically valid information. Moreover, managing
tured contextual reasoning layer via a formally specified cryptographickeysandcertificatesinlarge-scale,decentralized
|           |            |     |            |            |     |              | networks | like V2V | or P2P | environments | introduces |     | scalability, |
| --------- | ---------- | --- | ---------- | ---------- | --- | ------------ | -------- | -------- | ------ | ------------ | ---------- | --- | ------------ |
| selective | abstention |     | mechanism, | we achieve |     | expert-level |          |          |        |              |            |     |              |
contextual analysis without violating the strict latency revocation, and latency challenges [11]. These limitations
constraints of vehicular ingestion. highlight the need for complementary mechanisms such as
2) We provide the first quantitative analysis of the safety provenance verification, reputation assessment, and AI-driven
|            |     |            |             |            |               |        | reasoning   | to enhance | trust | and resilience | in  | decentralized | AV  |
| ---------- | --- | ---------- | ----------- | ---------- | ------------- | ------ | ----------- | ---------- | ----- | -------------- | --- | ------------- | --- |
| trade-offs |     | between    | traditional | reject-all | cryptographic |        |             |            |       |                |     |               |     |
| baselines  |     | and hybrid | AI systems. |            | We move       | beyond | ecosystems. |            |       |                |     |               |     |
simple accuracy metrics to offer a tiered risk-acceptance On the other hand, recent advances in artificial intelligence
framework(e.g.,conservativethresholdsforsafety-critical have introduced the concept of a Generative AI-driven driving
|     |     |     |     |     |     |     | assistant | agent, | which goes | beyond | traditional |     | perception |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------ | ---------- | ------ | ----------- | --- | ---------- |
kernelupdatesvs.permissivethresholdsforinfotainment),
providing a direct pathway for integrating AI-driven trust and decision-making to actively support cybersecurity in au-
into formal automotive safety cases. tonomous vehicles [12]. Unlike traditional rule-based systems,
3) We identify a pervasive label-leakage flaw in existing agenerativeAIagentcanunderstandcontext,simulatepotential
|     |          |            |       |               |     |              | threat scenarios, |     | and detect | anomalies | in  | system | behavior |
| --- | -------- | ---------- | ----- | ------------- | --- | ------------ | ----------------- | --- | ---------- | --------- | --- | ------ | -------- |
| AV  | security | benchmarks | where | maliciousness |     | is trivially |                   |     |            |           |     |        |          |
tied to metadata (e.g., ’FakeOEM’ IDs). We introduce [13]. During any information exchange, such an agent can
a novel, open-source dataset-generation grammar that supplement cryptographic validation by analyzing consistency
forces models to detect threats based on sophisticated and provenance information to identify suspicious patterns
|            |     |          |                |           |     |             | that may | suggest | rollback | attempts, | fake updates, |     | or malicious |
| ---------- | --- | -------- | -------------- | --------- | --- | ----------- | -------- | ------- | -------- | --------- | ------------- | --- | ------------ |
| behavioral |     | patterns | such as timing | anomalies |     | and version |          |         |          |           |               |     |              |
rollbacks—rather than simple identifier correlations. distributionchannels.Furthermore,generativemodelsfacilitate
Organization: The rest of the paper is organized as follows: adaptive learning from changing attack strategies, enabling
|         |            |                |     |        |                |     | the agent | to anticipate | new | adversarial | behaviors |     | and improve |
| ------- | ---------- | -------------- | --- | ------ | -------------- | --- | --------- | ------------- | --- | ----------- | --------- | --- | ----------- |
| Section | II depicts | the motivation |     | behind | this research. | We  |           |               |     |             |           |     |             |
resilienceovertime[14].Byintegratingthisintelligentassistant
| describe | the system | design | in Section | III. | Section | IV, and |     |     |     |     |     |     |     |
| -------- | ---------- | ------ | ---------- | ---- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- |
Section V explore the analysis, results, and discussions. We into the vehicle ecosystem, manufacturers can add an extra
discuss related works in Section VI, and this paper concludes layer of defense that dynamically assesses trustworthiness,
|            |      |     |            |     |     |     | enhances          | situational | awareness,  | and   | reduces        | reliance       | on static |
| ---------- | ---- | --- | ---------- | --- | --- | --- | ----------------- | ----------- | ----------- | ----- | -------------- | -------------- | --------- |
| in Section | VII. |     |            |     |     |     |                   |             |             |       |                |                |           |
|            |      |     |            |     |     |     | security          | measures    | alone. This | makes | the generative |                | AI-driven |
|            |      | II. | MOTIVATION |     |     |     |                   |             |             |       |                |                |           |
|            |      |     |            |     |     |     | driving assistant |             | a promising | tool  | for delivering | context-aware, |           |
Modernautonomousvehiclesarenolongerisolatedsystems. proactive cybersecurity for the next generation of autonomous
| They are | being | operated | as part | of a | vast and | dynamic | vehicles. |     |     |     |     |     |     |
| -------- | ----- | -------- | ------- | ---- | -------- | ------- | --------- | --- | --- | --- | --- | --- | --- |
information ecosystem [1]. Decisions, such as choosing a Combining Generative AI with traditional cryptography
route in response to an unexpected obstacle, depend on a opens a promising pathway. Cryptography can ensure that
2924
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.

| TABLE                   | I. Key   | Challenges | in                                  | Provenance-Aware |     | Trust for      |     |     |     |     |     |     |     |     |
| ----------------------- | -------- | ---------- | ----------------------------------- | ---------------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| Autonomous              | Vehicles |            |                                     |                  |     |                |     |     |     |     |     |     |     |     |
| Challenge               |          |            | Description                         |                  |     |                |     |     |     |     |     |     |     |     |
| InformationAuthenticity |          |            | Ensuringtheauthenticityandintegrity |                  |     |                |     |     |     |     |     |     |     |     |
|                         |          |            | of                                  | V2X messages     |     | from untrusted |     |     |     |     |     |     |     |     |
sources.
| ProvenanceVerification |     |     | Validatingdataprovenanceefficiently |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
andprivatelyindistributednetworks.
| DecentralizedTrustManage- |     |     | Decentralizedtrustmanagementamong   |     |     |     |      |             |           |     |        |            |       |     |
| ------------------------- | --- | --- | ----------------------------------- | --- | --- | --- | ---- | ----------- | --------- | --- | ------ | ---------- | ----- | --- |
| ment                      |     |     | dynamic,distributedparticipants.    |     |     |     |      |             |           |     |        |            |       |     |
| Multi-ModalDataFusion     |     |     | Evaluatingcross-modalconsistencyfor |     |     |     |      |             |           |     |        |            |       |     |
|                           |     |     |                                     |     |     |     | Fig. | 2. Proposed | AI-driven |     | hybrid | validation | model |     |
reliableV2Xdecisions.
| IntegrationwithAIModels |     |     | Robust | AI reasoning |     | over heteroge- |     |     |     |     |     |     |     |     |
| ----------------------- | --- | --- | ------ | ------------ | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
neousdatainuncertainenvironments.
Security–PrivacyTrade-off Balancingtransparentdataprovenance communications and updates in which messages from OEMs,
withvehicleprivacy. infrastructure, or V2V peers are signed and hashed; receivers
Interoperability Ensuringcross-vendorV2Xinteroper- verify signatures against a PKI and check integrity via hashes.
abilityforunifiedtrustevaluation. The diagram highlights authenticated channels, certificate
|     |     |     |     |     |     |     | authorities,       | and | validation | checkpoints        |       | that block | tampering |        |
| --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ---------- | ------------------ | ----- | ---------- | --------- | ------ |
|     |     |     |     |     |     |     | and impersonation. |     | On the     | other              | hand, | Fig. 2     | overlays  | an AI- |
|     |     |     |     |     |     |     | driven assistant   |     | atop the   | same cryptographic |       | substrate. |           | After  |
OTA Module P2P Module signatureandhashchecks,aprovenancelayercorrelatesissuer
Peer-to-Peer Network
Listens from
Data OTA P e e r s   f o r history, software lineage, and distribution paths; a reputation
| Collection | Network | Components Updating |     | avail a b l e   u p d | ates Peer 1 | Peer 2 |     |     |     |     |     |     |     |     |
| ---------- | ------- | ------------------- | --- | --------------------- | ----------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
modulescoressources;andananomalyengineinspectscontent
| Update | Update |     |     |     |     | .   .   .   .   . Peer n |     |     |     |     |     |     |     |     |
| ------ | ------ | --- | --- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- |
Notification Module Peer 4 forrollbackattempts,versionskew,andinconsistentcontext.A
|     |     |     |     | etadpu elbaliava stsacdaorB selcihev ybraen ot atadatem | Peer 3 |     |           |      |             |         |            |     |         |       |
| --- | --- | --- | --- | ------------------------------------------------------- | ------ | --- | --------- | ---- | ----------- | ------- | ---------- | --- | ------- | ----- |
|     |     |     |     |                                                         |        |     | reasoning | loop | fuses these | signals | to produce | a   | dynamic | trust |
Collects full
updates if
available  score and policy (accept, quarantine, or request escalation).
OTA Updates The figure emphasizes adaptive learning from emerging attack
|     |     |     |     |     |     |     | patterns, | yielding | proactive, | context-aware |     | resilience. |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------- | ---------- | ------------- | --- | ----------- | --- | --- |
Storing  & Managing OTA Updates
|     |     | Update Block |                | Update          | Advertising          |     |              |        |            |     |       |     |     |     |
| --- | --- | ------------ | -------------- | --------------- | -------------------- | --- | ------------ | ------ | ---------- | --- | ----- | --- | --- | --- |
|     |     | Repository   | Metadata       |                 | available updates to |     |              |        |            |     |       |     |     |     |
|     |     |              | H a sh         | D i g i t a l   | Peers                |     | A. AI Driven | Hybrid | Validation |     | Model |     |     |     |
|     |     |              | Da ta b ase Ce | r t if i c a te |                      |     |              |        |            |     |       |     |     |     |
Central Server
|               |             |               |     |             |        |                  | The AI-based   |            | driving    | assistant     | agent     | operates   | as             | a two- |
| ------------- | ----------- | ------------- | --- | ----------- | ------ | ---------------- | -------------- | ---------- | ---------- | ------------- | --------- | ---------- | -------------- | ------ |
| Fig. 1.       | Traditional | cryptographic |     | validation  |        | architecture     |                |            |            |               |           |            |                |        |
|               |             |               |     |             |        |                  | stage hybrid   | pipeline   | that       | explicitly    | separates |            | discriminative |        |
|               |             |               |     |             |        |                  | classification | from       | generative | reasoning,    |           | addressing | the            | fun-   |
|               |             |               |     |             |        |                  | damental       | tension    | between    | deterministic |           | security   | enforcement    |        |
| messages      | remain      | authentic     | and | unaltered   | during | transmission,    |                |            |            |               |           |            |                |        |
|               |             |               |     |             |        |                  | and adaptive   | contextual |            | analysis.     | In        | Stage 1,   | a fine-tuned   |        |
| but it cannot | verify      | the source’s  |     | credibility | or     | trustworthiness. |                |            |            |               |           |            |                |        |
ThisiswhereGenerativeAIcanmakeatransformativeimpact DistilBERT transformer [15] operates as a binary sequence
by analyzing various data inputs, learning from experience, classifier, serializing structured records from OTA update logs,
|              |                 |     |      |             |     |               | V2X message | metadata, |     | and provenance |     | chains | into natural- |     |
| ------------ | --------------- | --- | ---- | ----------- | --- | ------------- | ----------- | --------- | --- | -------------- | --- | ------ | ------------- | --- |
| and spotting | inconsistencies |     | that | traditional |     | methods might |             |           |     |                |     |        |               |     |
languagepromptsfollowingafixedschema.Themodeloutputs
| miss. A | Generative | AI–based | agent | can | support | cryptographic |     |     |     |     |     |     |     |     |
| ------- | ---------- | -------- | ----- | --- | ------- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
verification by assessing the context, reputation, and origin of a posterior probability P(malicious|prompt)∈[0,1] as the
informationbeforeitimpactsavehicle’sdecisions.Inspiredby primary trust signal, ensuring reproducibility and auditability
|             |           |            |               |            |                     |               | of per-decision |      | outputs    | given fixed | model | weights. | Stage   | 2   |
| ----------- | --------- | ---------- | ------------- | ---------- | ------------------- | ------------- | --------------- | ---- | ---------- | ----------- | ----- | -------- | ------- | --- |
| the promise | of        | generative | AI-driven     | reasoning, |                     | our framework |                 |      |            |             |       |          |         |     |
|             |           |            |               |            |                     |               | activates       | when | classifier | confidence  | falls | below    | θ =0.75 | or  |
| adopts a    | pragmatic | hybrid     | architecture: |            | a transformer-based |               |                 |      |            |             |       |          |         |     |
discriminativeclassifierforreal-timebehavioraldetection,com- when the cryptographic and AI layers produce conflicting
plemented by a structured contextual reasoning layer designed verdicts, employing a lightweight deterministic rule engine
|                |     |                 |     |           |               |      | that performs | three      | functions: | contextual |                | threat | assessment,   |     |
| -------------- | --- | --------------- | --- | --------- | ------------- | ---- | ------------- | ---------- | ---------- | ---------- | -------------- | ------ | ------------- | --- |
| to accommodate |     | full generative |     | reasoning | as automotive | edge |               |            |            |            |                |        |               |     |
|                |     |                 |     |           |               |      | evaluating    | provenance | metadata   |            | and behavioral |        | flags against |     |
hardware matures.
knownattackpatterns;anomalyscoring,computingaweighted
III. SYSTEMMODEL suspicionsignalfromtimingandversionfeatures;andevidence
SecuringinformationinAVsisimportantforsafeandsecure fusion, combining cryptographic proofs, reputation scores, and
|             |     |              |     |            |     |               | classifier | posteriors | into | a fused | trust | score T | ∈ [0,1] | via a |
| ----------- | --- | ------------ | --- | ---------- | --- | ------------- | ---------- | ---------- | ---- | ------- | ----- | ------- | ------- | ----- |
| operations. | But | it addresses | new | challenges |     | regarding the |            |            |      |         |       |         |         |       |
authenticity and trustworthiness of the information received. configurablefusionpolicy.Thisdesignisarchitectedasadrop-
Table I depicts the challenges posed in information process- in replacement for a full instruction-tuned generative model,
ing. Fig. 1 depicts a conventional security pipeline for AV deferred to future hardware-capable deployments.
2925
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.

First,thediscriminativereasoninglayerisadvisoryonly:its proof under a game-theoretic reputation adversary model is
outputadjuststheconfidenceintervalaroundthediscriminative identified as a priority for follow-on work. The reputation
verdict but cannot overturn a high-confidence cryptographic scoreforeachsourcesattimetiscomputedusingexponential
failure. Second, when the fused trust score T falls below temporal decay:
a hard threshold θ (set conservatively at 0.40 based on
0 1 (cid:88)
validation performance), the system defaults to quarantine R
s
(t)=
Z
w
i
·o
i
·e−λ(t−ti)
mode, escalating to human oversight or issuing a hold request i
to the requesting module. Third, all generative outputs are wherew istheinteractionweight,o ∈+1,−1denotesthe
i i
logged with entropy scores; high-entropy outputs (indicating correctness of the validation outcome, λ=0.01 is the decay
model uncertainty) are automatically flagged and excluded constant, and Z is the normalization factor. This formulation
from automated policy enforcement. This selective abstention
ensures that recent interactions dominate the reputation score
mechanism ensures that the generative component degrades
while older observations gracefully lose influence. This for-
gracefully under distribution shift or novel attack patterns,
mulation ensures that: (i) nodes that have been inactive for
consistent with emerging automotive AI safety guidance [16].
extended periods experience gradual reputation neutralization
In summary, the agent architecture combines the determinism
ratherthanretentionofstaletrust;(ii)recentinteractionscarry
andauditabilityoftransformer-basedclassificationwiththecon-
proportionally greater weight; and (iii) a single malicious
textual adaptability of generative reasoning, without allowing
interaction cannot immediately reduce a high-reputation node
probabilistic generative outputs to override hard cryptographic
tozero(providingrobustnessagainstsingle-targeteddefamation
guarantees. Fig. 2 demonstrates this two-stage architecture.
events.Anode’sreputationdropsbelowaquarantinethreshold,
B. Adversarial Reputation Attacks: Sybil and Collusion Resis- its communications are automatically routed to enhanced
tance inspection mode regardless of cryptographic validity. These
nodes and their messages are rejected without AI inspection,
Sybil attacks, in which an adversary creates multiple
reducing computational load.
pseudonymous identities to artificially inflate collective rep-
utation or dilute honest node scores, are a fundamental C. Latency, Compute, and Bandwidth Feasibility
threat to vehicular reputation systems. The reputation system
Transformer-based inference on resource-constrained AV
implements a multi-heuristic Sybil detection mechanism that
hardware is a recognized deployment challenge. We evaluate
evaluates each update source along three dimensions:
the latency feasibility of our two-stage pipeline using an
1) Sourceswithfewerthanaconfigurableminimumnumber NVIDIA Tesla T4 GPU, measuring across the full test set
of observed interactions (default: 5) are automatically of 10000 samples. Stage 1 employs a fine-tuned DistilBERT
flagged as suspicious, preventing newly spawned Sybil classifier (66M parameters), which, when quantized to INT8
identities from immediately gaining trust. for edge deployment, is estimated to achieve 14-18 ms per
2) Eachsourceisrequiredtodemonstrateinteractionsacross prompt on an NVIDIA Xavier NX platform (21 TOPS). OTA
a minimum number of distinct communication channels updateacceptancedecisionsarenon-real-timepolicydecisions
(e.g., OTA, P2P, charging station). This counters Sybil’s madebeforeapplyinganupdateratherthanwithinthevehicle’s
identities that operate through a single fabricated channel. controlloop;IEEE1609.2advisoryoperationspermitlatencies
3) Sources exhibiting perfectly uniform validation outcomes up to 1,000 ms for V2I channels, and our combined pipeline
(all correct or all incorrect) beyond a minimum history satisfies this budget with significant margin.
length are flagged for potential track-record inflation, For V2V safety-critical messages (e.g., emergency alerts),
a known Sybil strategy in which fabricated identities we implement a fast-path mode that bypasses Stage 2 and
build artificial trust by participating only in unambiguous relies solely on the Stage 1 classifier and cryptographic
transactions. verdict, ensuring sub-100 ms response in line with V2V
Collusion attacks, in which a set of legitimate or compro- timing requirements. Stage 2 in the current implementation
mised nodes coordinate to inflate each other’s scores while is a lightweight, deterministic rule engine that evaluates the
targeting honest nodes with defamation, are addressed via the provenancemetadata,reputationscore,andStage1confidence
cluster anomaly detection mechanism above, combined with without invoking any additional neural model, achieving a
a defamation resistance threshold: a node’s reputation cannot meanlatencyofjust0.035msontheT4platform.Thisdesign
decrease by more than ∆R = 0.15 per time window as a choice, deferring generative reasoning to an asynchronous
max
result of reports from a single cluster of coordinated sources. advisorypath,ensuresthattheAIcomponentneverintroduces
This limits targeted defamation rates even when a collusive unacceptable delay on the safety-critical path. Should a full
coalition controls a substantial fraction of local reputation instruction-tuned generative model (e.g., 350M parameters)
reporters. We acknowledge that these mechanisms provide be deployed in Stage 2 in future hardware-constrained con-
heuristic rather than formal guarantees, and that sophisticated figurations, we estimate an additional 80-120 ms of overhead
adaptive adversaries may evade detection. A formal security on an Xavier NX-class platform, which remains acceptable
2926
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore. Restrictions apply.

for the asynchronous advisory mode. Regarding V2X channel communication environments, drawing on published vehicular
bandwidth,theprovenancemetadataappendedtoeachmessage network threat models and OTA update security studies [17].
(source certificate hash, version lineage vector, hop-count, and The dataset comprises 10,000 records generated from nine
behavioral flags) totals approximately 512 1,024 bytes per communication channel types: OTA server updates, P2P
message, representing less than 2% overhead relative to the peer exchanges, charging station communications, nearby-car
ETSI ITS-G5 WSMP maximum payload of 2,304 bytes. This V2V messages, parking garage infrastructure, police station
overhead is within acceptable bounds for V2V periodic coop- channels, traffic sight feeds, weather station data, and flood
erative awareness messages (CAMs), and all AI inference is alert broadcasts. Node roles are drawn from a neutral vocab-
performed locally on the vehicle; only the binary accept/reject ulary (participant, node, entity, peer, actor) and
verdict is communicated, preserving privacy. service providers from nine realistic organizational identifiers
(e.g., OEM, TrafficMgmt, WeatherSvc, PoliceDept),
D. Standards Alignment (IEEE 1609.2 and ETSI ITS)
with no identity field carrying intrinsic label information.
The cryptographic provenance layer is anchored to estab- Each record is synthesized by the following four-step
lished vehicular security standards. Message authentication procedure. First, a base metadata tuple is instantiated by
and certificate handling follow IEEE 1609.2-2022 for North independently sampling: a discrete timestamp t∼U{1,500},
AmericanV2Xdeployments,whichspecifiestheelliptic-curve a node identifier drawn from a pool of 100 logical nodes, a
digital signature algorithm (ECDSA) with P-256 or P-384 communication channel, a service provider, a version number
curves, pseudonym certificate management, and certificate v ∼ U{1,35}, and a routing path length ℓ (sampled from
revocation via Misbehavior Reporting. For European ITS U{2,8} for peer channels and U{1,4} for infrastructure
compatibility, the framework additionally supports ETSI TS channels to reflect realistic topology constraints). Second,
103 097 v2.1.1 secure message formats, including the ITS- cryptographic feature vectors are sampled conditionally on
AID(ApplicationIdentifier)fieldusedtovalidatethatmessage theattackscenario,withbenignsamplespassingcryptochecks
content type matches the declared application context, a field at 92-95% rates and attack samples exhibiting failure rates
directly leveraged by our contextual inconsistency detection tuned per attack sophistication. An LLM behavioral score is
rule. The trust management component aligns with ETSI TR additionallysampledfromaGaussiandistributionwhosemean
102 941, which defines a certificate trust list (CTL) structure is conditioned on the attack type: µ=0.75 for AI-detectable
forITScredentialmanagementsystems.Ourreputationmodule attacks (sophisticated/context inconsistency) and µ=0.40 for
is designed as a complementary layer atop this PKI infras- crypto-visible attacks (timing/rollback), ensuring the classifier
tructure: it operates on pseudonymous certificate identifiers cannot exploit a trivially separable score feature. Third, a
without requiring de-anonymization, thereby respecting the deterministic labeling function assigns maliciousness if any of
unlinkability properties guaranteed by pseudonym rotation. seven attack-scenario predicates is satisfied, each gated by an
Privacy-preserving reputation aggregation necessary to avoid independent Bernoulli trial to control prevalence:
re-identification through reputation score correlation across • Timing attack (p = 0.05): timestamp t > 450 and
pseudonym epochs is identified as a subject for future work. version v < 5, representing a stale-replay attack late
in the deployment timeline.
IV. EXPERIMENTALSETUP
• Version rollback (p = 0.03): v > 25 and t < 50,
The research employs a comprehensive simulation dataset indicating a high-version update appearing anomalously
derived from autonomous vehicle scenarios, specifically de- early,consistentwithacompromised-but-legitimate-OEM
signedtoevaluatetheeffectivenessofhybridAI-cryptographic rollback vector.
validation systems in detecting sophisticated attacks that • Pathmanipulation(p=0.04):routingpathlengthℓ>6
may bypass traditional security measures. The dataset com- over a P2P channel, indicating an abnormally deep relay
prises approximately 10,000 meticulously crafted entries that chain inconsistent with the declared distribution topology.
represent realistic V2V and vehicle-to-infrastructure (V2I) • Context inconsistency (p = 0.03): PoliceDept
communication scenarios across diverse operational contexts, provider distributing a very high-version firmware (v>
includingOTAupdates,P2Pnetworks,chargingstations,traffic 30),oraWeatherSvcnoderoutingoveraP2Pchannel
managementsystems,weatherservices,policecommunications, both representing service-type/channel mismatches.
andemergencyalertchannels.Eachdatasetentryencompasses • Infrastructure compromise (p = 0.02): a charging
criticalcontextualfeatures,includingtemporalidentifiers,node station or parking garage channel carrying a high-version
classifications, communication pathways, routing path lengths, update (v>28), targeting physical-layer attack surfaces.
and service provider organizations. • Sophisticated/unknown attack (p=0.08): a composite
behavioralscore(tmod7)+(vmod5)+(ℓmod3)>8,
A. Dataset Construction Methodology
representing complex multi-field anomalies that evade
The simulation dataset was constructed using a structured rule-based detectors but may be learnable by a trained
generative grammar designed to approximate realistic AV classifier.
2927
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore. Restrictions apply.

Random catch-all (p=0.15): an independent Bernoulli vehicular network threat models, with all key parameters
•
trial applied to remaining benign-labeled samples to chosen systematically: the class balance of 80% benign and
achieve a target class balance of approximately 20% 20% malicious reflects operationally realistic CAV threat
malicious. prevalence; the decay constant λ = 0.01 is calibrated to
|         |         |           |     |       |            |          |     | ensure stale | interactions | retain | less than 1% influence | over a |
| ------- | ------- | --------- | --- | ----- | ---------- | -------- | --- | ------------ | ------------ | ------ | ---------------------- | ------ |
| Fourth, | records | for which | all | seven | predicates | evaluate | to  |              |              |        |                        |        |
false are labeled benign (is malicious=0). A 10% additive 499-step horizon; and confidence thresholds θ = 0.75 and
Gaussian perturbation is applied to t, v, and ℓ on a random θ = 0.40 were determined through validation-set tuning
0
|                 |         |              |          |              |                    |     |        | to balance | Stage 2            | activation | rate against latency | and false- |
| --------------- | ------- | ------------ | -------- | ------------ | ------------------ | --- | ------ | ---------- | ------------------ | ---------- | -------------------- | ---------- |
| subset of       | samples | to introduce |          | realistic    | measurement        |     | noise, |            |                    |            |                      |            |
|                 |         |              |          |              |                    |     |        | negative   | risk. To partially | assess     | generalizability,    | we apply   |
| with all values | clamped |              | to their | valid ranges | post-perturbation. |     |        |            |                    |            |                      |            |
Chain-integrityconsistencyisenforcedstructurally.Toaddress a leave-one-context-out robustness protocol, withholding one
data leakage identified in preliminary experiments, all explicit entire communication context category during training and
adversary FakeOEM evaluating on it at test time, reporting a 6.3 percentage-point
| adversarial          | markers | (e.g., |          |               | role labels, |     |          |          |               |                    |              |       |
| -------------------- | ------- | ------ | -------- | ------------- | ------------ | --- | -------- | -------- | ------------- | ------------------ | ------------ | ----- |
|                      |         |        |          |               |              |     |          | accuracy | drop relative | to in-distribution | performance, | which |
| creator identifiers) |         | were   | removed; | maliciousness |              | is  | inferred |          |               |                    |              |       |
exclusively from behavioral feature patterns. serves as a controlled proxy for covariate shift. Validation
A post-generation correlation audit confirmed that no role against instrumented ETSI ITS-G5 testbeds or USDOT V2X
|     |     |     |     |     |     |     |     | pilot deployment | traces | is identified | as the | primary target |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | ------ | ------------- | ------ | -------------- |
orcreatorfieldachievedamalicious-ratecorrelationexceeding
|                 |     |         |     |           |             |     |          | for follow-on | work, | including | planned collaboration | with an |
| --------------- | --- | ------- | --- | --------- | ----------- | --- | -------- | ------------- | ----- | --------- | --------------------- | ------- |
| 0.8, validating | the | absence | of  | trivially | exploitable |     | surface- |               |       |           |                       |         |
level features. The overall class balance is approximately 80% automotive OEM partner for field data collection.
benignand20%malicious,reflectinganoperationallyrealistic
V. RESULTSANDIMPLEMENTATION
| threat prevalence |     | for connected |     | AV  | environments. |     | Among |                   |     |     |     |     |
| ----------------- | --- | ------------- | --- | --- | ------------- | --- | ----- | ----------------- | --- | --- | --- | --- |
|                   |     |               |     |     |               |     |       | A. Implementation |     |     |     |     |
malicioussamples,timinganomaliesaccountfor31%,version
rollbacks for 24%, path manipulation for 19%, contextual The traditional cryptographic validation system implements
inconsistenciesfor14%,infrastructurecompromisefor8%,and industry-standardsecuritymechanisms,includingdigitalsigna-
|            |            |     |     |            |          |        |      | ture verification, | hash-based | integrity | checking, | and certificate- |
| ---------- | ---------- | --- | --- | ---------- | -------- | ------ | ---- | ------------------ | ---------- | --------- | --------- | ---------------- |
| reputation | mismatches | for | 4%. | Stratified | sampling | across | both |                    |            |           |           |                  |
class and attack type is used for all train/validation/test splits based authentication protocols. This system operates through
(70%/10%/20%) to prevent distribution mismatch between rule-based logic that validates cryptographic proofs of authen-
partitions. The dataset is synthetic and does not claim to repli- ticity, ensures roll-forward protection against replay attacks,
|                 |     |           |                |     |       |             |     | and verifies | chain-of-custody |     | integrity. However, | by design, |
| --------------- | --- | --------- | -------------- | --- | ----- | ----------- | --- | ------------ | ---------------- | --- | ------------------- | ---------- |
| cate real-world | AV  | telemetry | distributions. |     | Known | constraints |     |              |                  |     |                     |            |
include approximately uniform channel and creator sampling this approach cannot assess the trustworthiness or malicious
(whereas real deployments skew toward OTA and V2V chan- intent of legitimate but compromised sources, representing the
nels), engineered rather than empirically measured attack-type core limitation this research seeks to address. In contrast,
|              |         |         |     |          |              |     |         | the AI-enhanced | validation |     | system leverages | a fine-tuned |
| ------------ | ------- | ------- | --- | -------- | ------------ | --- | ------- | --------------- | ---------- | --- | ---------------- | ------------ |
| prevalences, | and the | absence | of  | temporal | correlations |     | between |                 |            |     |                  |              |
successive updates from the same node. The grammar is open- DistilBERT transformer model trained on natural language
sourced to enable researchers to reparameterize distributions descriptions of different scenarios. The model processes
for their deployment context. contextual information, including communication patterns,
|               |          |     |              |     |       |             |     | source behavior, | and        | environmental | factors, to   | generate trust |
| ------------- | -------- | --- | ------------ | --- | ----- | ----------- | --- | ---------------- | ---------- | ------------- | ------------- | -------------- |
| B. Ecological | Validity | and | Distribution |     | Shift | Limitations |     |                  |            |               |               |                |
|               |          |     |              |     |       |             |     | scores that      | complement | traditional   | cryptographic | validation.    |
We acknowledge that synthetic simulation datasets raise This approach enables the detection of subtle anomalies and
inherent concerns about ecological validity, and that val- suspicious patterns that may indicate malicious intent even
idation against real-world vehicular communication traces when cryptographic validation passes, particularly in scenarios
would further strengthen the framework’s credibility. Publicly involving compromised legitimate entities such as OEMs or
available real-world V2X datasets, such as V2AIX [18], a infrastructure providers.
multi-modal ETSI ITS message corpus gathered from public The dataset specifically includes critical test cases where
road traffic, provide authentic communication captures but cryptographically valid information originates from legitimate
contain no labeled adversarial traces for the specific attack sources but carries malicious payloads, representing the exact
categories modeled here, namely timing anomalies, version scenarios where traditional cryptographic systems fail. These
rollbacks, path manipulation, and context inconsistencies, as entriesdemonstratereal-worldattackvectorswhereadversaries
thesearebydefinitionrare,infrastructure-level,ordeliberately compromise legitimate infrastructure or impersonate trusted
injected events that do not manifest in benign operational cap- entities while maintaining cryptographic validity. The AI com-
tures. Consequently, simulation-driven evaluation remains the ponent’s ability to identify these scenarios through contextual
methodologicalnorminAVandV2Xsecurityresearch,where analysis and behavioral pattern recognition demonstrates that
ground-truth attack labeling is infeasible without controlled hybrid AI-cryptographic validation can deliver essential secu-
injection. Our dataset construction grammar is designed to rity capabilities beyond purely cryptographic approaches. The
approximaterealisticthreatdistributionsdrawnfrompublished experimental methodology employs standard machine learning
2928
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.

practices with stratified train-validation-test splits, ensuring indicates balanced performance, with the system successfully
both systems are evaluated on identical data distributions. identifying malicious updates while maintaining an acceptable
Performance metrics include accuracy, precision, recall, F1- false alarm rate. The key improvements arise from the AI
score, and specialized analyses of false-positive and false- component’s ability to detect sophisticated attacks through
negative rates across different attack categories. This rigorous behavioral pattern recognition, identifying timing anomalies,
evaluation framework enables a quantitative demonstration version rollback attempts, path manipulation, and contextual
of the AI-enhanced system’s superior capability in detecting inconsistencies that purely cryptographic validation may miss.
sophisticated attacks that exploit the inherent limitations of Thefusion strategydynamically weightsAIand cryptographic
purelycryptographicvalidationapproachesindecentralizedau- inputs based on attack type, with AI authority increasing for
tonomousvehiclenetworks.Alltherelevantcodesarepublicly behavioral anomalies (e.g., timing, context) and cryptographic
available and can be reproduced using https://github.com/cps- validation dominating for traditional security violations.
security-703/Provenance-Aware-Trust-Framework. Fig. 4(b) demonstrates the operational trade-offs between
|               |         |     |     |     | the two validation |      | approaches.    | The | traditional method | exhibits  |
| ------------- | ------- | --- | --- | --- | ------------------ | ---- | -------------- | --- | ------------------ | --------- |
| B. Simulation | Result: |     |     |     |                    |      |                |     |                    |           |
|               |         |     |     |     | a prohibitively    | high | false-positive |     | rate (≈90.7%)      | with zero |
1400 falsenegatives,generatingroughly4.7falsealarmspergenuine
1400
156 1521 1200 1538 139 1200 threat, while the AI-based model reduces this to 8.29% false
| 0   |     | 0   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1000 1000 positives and a modest 21.67% false-negative rate, and an 11-
| lautcA |     | lautcA |     |     |                                                        |     |     |     |     |     |
| ------ | --- | ------ | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- |
|        |     | 800    |     | 800 |                                                        |     |     |     |     |     |
|        |     | 600    |     |     | foldreductioninspuriousalerts.TheROCanalysisinFig.4(c) |     |     |     |     |     |
600
1 0 323 400 1 70 253 further illustrates this architectural contrast: the AI-based
400
200 fusion model achieves an AUC of 0.937, reflecting calibrated
200
0 1 0 0 1 confidencescoringacrossvaryingdecisionthresholds,whereas
|     | Predicted |     | Predicted |     |     |     |     |     |     |     |
| --- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
(a) (b) the traditional cryptographic system is confined to a single
Fig. 3. (a) Confusion matrix of the traditional cryptographic fixed operating point (FPR=0.907, TPR=1.00), as signature
method and (b) combined fusion model with AI-based hybrid verification systems lack a tunable threshold and cannot pro-
|     |     |     |     |     | duce a meaningful |     | ROC curve. | While | traditional | cryptography |
| --- | --- | --- | --- | --- | ----------------- | --- | ---------- | ----- | ----------- | ------------ |
validation
|     |     |     |     |     | provides deterministic |     | guarantees |     | at that fixed | point, the AI- |
| --- | --- | --- | --- | --- | ---------------------- | --- | ---------- | --- | ------------- | -------------- |
We evaluate a provenance-aware trust framework for AV augmented approach enables risk-adaptive decision-making
information ingestion that integrates cryptographic provenance across the full ROC space.
|              |                   |                     |     |            | While the | traditional | cryptographic |     | baseline | achieves zero |
| ------------ | ----------------- | ------------------- | --- | ---------- | --------- | ----------- | ------------- | --- | -------- | ------------- |
| verification | with a fine-tuned | AI agent performing |     | behavioral |           |             |               |     |          |               |
consistencychecksandcontextualanomalydetection,andcom- FN, it does so by classifying almost all inputs as malicious,
pare it with a cryptographic-only baseline. The evaluation ad- yielding a 90.7% false positive rate (FP=1,521). In practice,
dresses data leakage issues through realistic dataset generation this blocks critical safety patches and causes alert fatigue,
|                 |                |            |        | adversary | making the | baseline’s | zero-FN | guarantee | an operational | safety |
| --------------- | -------------- | ---------- | ------ | --------- | ---------- | ---------- | ------- | --------- | -------------- | ------ |
| that eliminates | obvious attack | indicators | (e.g., |           |            |            |         |           |                |        |
roles,FakeOEMcreators)andbasesmaliciousnessonsophisti- hazard. In contrast, the AI-based model introduces 70 FNs
catedbehavioralpatternsratherthanperfectcorrelations.Inthe (a 21.67% miss rate). However, this risk is mitigated at the
testpartition,thetraditionalcryptographicmodeldemonstrates architectural level. The AI operates as a secondary defense;
|                |           |                   |           |           | standard signature |     | failures | are caught | by cryptography | before |
| -------------- | --------- | ----------------- | --------- | --------- | ------------------ | --- | -------- | ---------- | --------------- | ------ |
| a conservative | approach, | achieving perfect | malicious | detection |                    |     |          |            |                 |        |
(true negative (TN)=156, false negative (FN)=0) at the cost of reachingtheAI.Furthermore,low-confidenceverdicts(T ≤θ 0 )
excessive false alarms (false positive(FP)=1,521) (Fig. 3(a)). default to quarantine. The 70 FNs predominantly involve
Thisaggressiveflaggingstrategyresultsinafalse-positiverate infrastructure compromises cryptographically valid but behav-
iorallyanomalousinputs,wherethebaselinepracticallyfailsby
| of 90.7% | while maintaining | 100% recall, | giving | an overall |     |     |     |     |     |     |
| -------- | ----------------- | ------------ | ------ | ---------- | --- | --- | --- | --- | --- | --- |
precisionofonly17.52%.Thisindicatesanoverlyconservative rejectingeverything.TomanageFNrisk,werecommendarisk-
validation strategy that flags nearly all updates as potentially stratifiedpolicyalignedwithISO26262HARAoutcomes,with
malicious to avoid missing genuine threats. Consequently, the aconservativethreshold(θ=0.85)forsafety-criticalfirmware
|     |     |     |     |     | and a permissive |     | threshold | (θ = | 0.55) for low-consequence |     |
| --- | --- | --- | --- | --- | ---------------- | --- | --------- | ---- | ------------------------- | --- |
lowaccuracy(23.95%)createsasubstantialoperationalburden
duetoexcessivefalsealarms,renderingthesystemimpractical updates like map data. A formal fault tree analysis is planned
| for deployment. |              |               |        |          | as a near-term | deliverable. |     |     |     |     |
| --------------- | ------------ | ------------- | ------ | -------- | -------------- | ------------ | --- | --- | --- | --- |
| By contrast,    | the AI-based | cryptographic | fusion | approach |                |              |     |     |     |     |
achieves significantly improved performance, as shown in C. Evaluation of Reputation System
Fig. 3(b), achieving balanced performance with TN=1,538, FP We have evaluated the reputation component to explicitly
= 139, FN = 70, and TP = 253, yielding 89.55% accuracy. address Sybil attacks, collusion, and temporal decay, all well-
Mostnotably,specificityimprovesto91.71%(anearly10-fold documentedthreatsinvehicularnetworks.Inourexperimental
increase compared to the baseline’s 9.3%), reducing false- evaluation across 10,000 update samples from 9 distinct
positive rates to 8.29% (Fig. 4(a)). The F1-score of 0.708 sources, all legitimate sources were correctly cleared after
2929
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.

1.0
0.8
0.6
0.4
0.2
0.0 Accuracy Precision Recall F1 Score Specificity
Performance Metrics
erocS
1.000 0.895 0.917
0.783 0.8
0.708
0.645
0.6 Traditional Crypto AI-Based Crypto
0.298 0.4
0.239
0.175 0.093 0.2
0.0 Traditional AI-Based Crypto Crypto
Validation Method
(a)
etaR
rorrE
0.907 False Positive Rate 1.0 False Negative Rate
0.8
0.6
0.4
0.217
0.083 0.2 0.000 0.00.0 0.2 0.4 0.6 0.8 1.0
False Positive Rate
(b)
etaR
evitisoP
eurT
AI-Based Crypto (AUC = 0.937) Traditional Crypto (Fixed Point: FPR=0.907, TPR=1.000) Random Classifier
(c)
Fig. 4. Demonstrating (a) performance analysis, (b) validation of traditional cryptographic methods with a combined fusion
model with a generative AI model and (c) comparative ROC-AUC
TABLE II. Per-Source Reputation Scores (decay λ=0.01) channelcommunicationpatternandrobustinteractionhistories
provide strong evidence that none of the network entities
Source Reputation Interactions Channels Sybil?
exhibit malicious Sybil behavior. Our temporal decay analysis
ServiceProvider 0.8782 1177 1 ✓No shown in Table III confirms that the most recent 20% of
UpdateSource 0.8857 1124 1 ✓No
SystemEntity 0.8905 1091 1 ✓No interactions contribute approximately 62–65% of the total
OEM 0.8948 1103 1 ✓No decayed weight across all sources, demonstrating effective
NetworkNode 0.8961 1048 1 ✓No recency bias. The effective decay over the full observation
TrafficMgmt 0.8991 1108 1 ✓No
WeatherSvc 0.9003 1061 1 ✓No span of 499 timesteps is 0.9932, meaning early interactions
TechProvider 0.9008 1112 1 ✓No retain less than 1% of their original influence, ensuring that a
PoliceDept 0.9009 1176 1 ✓No previously compromised source cannot rely on stale trust.
TABLE III. Temporal Decay Analysis (λ=0.01)
TABLE IV. Latency Performance by Pipeline Stage
Source Recent20%Wt ObsSpan Eff.Decay
Stage Mean P50 P95 Max
NetworkNode 61.96% 499 0.9932
OEM 63.63% 499 0.9932 DistilBERT 40.72ms 37.36ms 52.30ms 248.64ms
PoliceDept 62.42% 499 0.9932 ReasoningEngine 0.035ms 0.033ms 0.047ms 0.14ms
ServiceProvider 62.81% 499 0.9932
SystemEntity 62.06% 499 0.9932 Combined 40.76ms — 52.35ms —
TechProvider 63.95% 499 0.9932
TrafficMgmt 62.72% 499 0.9932
UpdateSource 62.69% 499 0.9932 D. Deployment Feasibility
WeatherSvc 65.53% 499 0.9932
Theframeworkemploysatwo-stageinferencepipelinewith
the measured latency characteristics (evaluated over 10,000
accumulating sufficient interaction history (≥1,000 interac- samples)showninTableIV.Webenchmarkourlatencyagainst
tions each), while the detection mechanisms remain active the timing requirements specified in IEEE 1609.2 and ETSI
for newly appearing or anomalous sources. We implement ITS. The latency distribution of the Stage 1 discriminative
pairwise collusion detection by analyzing the agreement classifier demonstrates a P95 latency of 52.30 ms, rigorously
rate of validation verdicts across all source pairs within a satisfyingthestringent100msrequirementdelineatedinIEEE
configurable time window. Source pairs with an agreement 1609.2 with a substantial margin of 47.7 ms. Furthermore,
rate exceeding a threshold (default: 85%) are flagged for to accommodate ultra-low-latency V2V safety dissemination
potential coordinated behavior. In our evaluation, no source scenarios(e.g.,pre-crashsensing),thearchitectureincorporates
pairs exceeded this threshold, indicating diverse and inde- anadaptivefast-pathmode.ThismodeactivelybypassestheAI
pendent prediction patterns across sources, consistent with inferencepipeline,relyingexclusivelyonthehighlyoptimized
the absence of injected collusion in the test dataset. The cryptographic validation layer to achieve sub-millisecond
evaluation results shown in Table II indicate consistently high processing latency or infrastructure-to-vehicle updates (e.g.,
reputation scores across all monitored sources, ranging from trafficsignaltiming,routinefirmwaredissemination).Theend-
0.8782 to 0.9009, demonstrating stable trust levels across to-end execution of the full two-stage pipeline, including both
interactionvolumesexceeding1,000perentity.Incorporatinga the transformer-based classifier and the generative reasoning
temporal decay factor of λ=0.01, the assessment framework layer, yields a P95 latency of 52.35 ms. This performance
effectively maintains current reputation standings without profilecomfortablysatisfiesthe1,000msETSIITSconstraint,
disproportionatehistoricaldegradation.Furthermore,thesingle- securing an operational buffer exceeding 947 ms.
2930
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore. Restrictions apply.

The Stage 1 classifier uses DistilBERT (66M parameters, networking (NDN), which provides a better foundation for
268 MB model size), which is compatible with automotive- secure data sharing among autonomous vehicles. Rathee et al.
grade edge computing platforms such as the NVIDIA Jet- [20]addressthesecurityofsmartsensorsinconnectedvehicles
son Orin and Xavier NX. Peak memory consumption is by proposing a blockchain framework to secure information
approximately 500 MB (model, tokenizer, and inference exchange. Maeng et al. [21] analyzes the types of information
batch). Stage 2 is entirely rule-based and requires no GPU security threats and proposes solutions to protect consumers’
resources,completingin≈0.04ms.Theframeworkisdesigned connected and autonomous vehicles (CAVs) from such threats.
with bandwidth efficiency and privacy preservation as core Parekh et al. [22] examine the current state of research and
principles.Eachtransmittedupdateencapsulatesapproximately development in environmental detection, pedestrian detection,
512–1,024bytesofprovenancemetadata(e.g.,creatoridentity, path planning, motion control, and vehicle cybersecurity for
communication channel, version lineage, path length, and autonomousvehicles.Chowdhuryetal.[17]buildsanelaborate
temporalmarkers).Thisminimalfootprintoperatescomfortably threat model to make the OTA update information trustworthy
within the payload capacities of DSRC (Dedicated Short- in AVs.
Range Communications) and cellular-V2X channels, ensuring
Gupta et al. [4] investigate a common attack taxonomy
negligiblenetworkcongestion.Alltransformer-basedinference
for emerging cyber threats, leveraging the immense amount
and subsequent analysis are executed strictly on-vehicle.
of actionable information from CAVs. Sun et al. [23] pro-
Consequently, no raw provenance data or granular log content
poses a tamper-resistant broadcasting (TRBS) scheme for
is ever transmitted over externally facing V2X communication
secure communication, which can protect data from being
links. To secure the privacy of the original provenance trail,
illegally accessed, forged, or tampered with by malicious
only the conclusive binary validation verdict (accept or reject)
vehicles, and enables efficient and flexible secure information
is propagated to the broader network infrastructure.
dissemination between autonomous vehicles. Gonc¸alves et
To secure the AI components against adversarial input
al. [24] presents how to secure the information between the
manipulation, the framework integrates structural constraints
several communicating nodes of a platoon by using a security
that limit input sequences to a maximum of 512 tokens, effec-
model for a Vehicular Ad hoc Network. Pradhan et al. [25]
tivelymitigatingbuffer-overflowandextendedcontext-injection
studies the design, simulation, and analysis of a quantum
vulnerabilities. The Stage 1 classifier operates exclusively in
cryptographic protocol employing quantum key distribution
a fixed-class discriminative mode (binary classification). The
(QKD) for secure key exchange. Alam et al. [26] investigates
absence of a free-form, generative prompt interface inherently
related data security and privacy research in CAVs using the
neutralizespromptinjectionvectorscommonlyassociatedwith
cryptographic Blockchain-enabled Federated Reinforcement
large language models. The Stage 2 counterfactual reason-
Learning (BFRL) framework. Raiyn et al. [27] examine iris
ing layer fundamentally relies on predefined, parameterized
recognition for securing data communication in AV networks,
templates rather than open-ended language generation. As an
using cryptography for information transmission via message
adversarycanonlyinfluencethespecificextractednumericalor
protocols and authentication.
categorical features, the scope for manipulating the generated
explanatory narrative is deterministic and strictly localized. While several prior hybrid frameworks have explored the
Updates receiving a confidence score below the quarantine intersection of AI and cryptography for AV security, a direct
threshold(default:0.40)areautomaticallyescalatedformanual quantitative comparison is constrained by the absence of
reviewratherthansilentlyaccepted.Inourevaluation,170out shared benchmarks and publicly available implementations.
of2,000testsamples(8.50%)werequarantined,demonstrating Bendiab et al. [28] integrate blockchain and AI for AV trust
that the system errs on the side of caution when verdicts are but do not address latency-bounded inference or provenance
uncertain. The quarantine threshold and decision threshold are chain tracking. Khan et al. [29] apply GenAI to intelligent
configurable per update category (e.g., safety-critical firmware transportation systems but lack formal Sybil resistance and
vs. infotainment), enabling risk-stratified deployment aligned risk-stratified thresholding. Ahmed et al. [30] focus on AI-
with the criticality hierarchy in ISO/SAE 21434. based anomaly detection without cryptographic provenance
anchoring or reputation modeling. Guntuka et al. [31] outlines
VI. RELATEDWORKS
the current state of GenAI in vehicular network cybersecurity
Thesecurityofautonomousvehicleshasbeenagrowingarea and establishes clear protocols for data privacy, ensuring
ofresearchastheybecomeincreasinglyintegratedintocritical transparency in AI decision-making processes. The proposed
operations. To secure information, traditional techniques have framework uniquely integrates all four dimensions of dual-
beenfoundtoposesignificantchallenges,includingcontextual stage AI inference within IEEE 1609.2 latency budgets,
inconsistencies, misleading provenance tracking, and so on. exponential-decay reputation modeling with multi-heuristic
In this regard, hybrid AI-cryptographic validation frameworks Sybil resistance, cryptographic provenance chain verification,
have emerged as a promising solution. Chowdhury et al. [19] and ISO 26262–aligned risk-stratified policy, distinguishing it
proposes a new data-centric Internet architecture, named data architecturally from existing approaches.
2931
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore. Restrictions apply.

VII. CONCLUSION [11] A. Z. A. Aljarwan and M. A. B. Ngadi, “Review of certificateless
|            |            |     |                    |     |       |           |     | authentication |     | scheme for | vehicular | ad hoc | networks,” | IEEE | Access, |
| ---------- | ---------- | --- | ------------------ | --- | ----- | --------- | --- | -------------- | --- | ---------- | --------- | ------ | ---------- | ---- | ------- |
| This paper | introduced |     | a provenance-aware |     | trust | framework |     |                |     |            |           |        |            |      |         |
2025.
| that bridges  | the        | gap between | static   | cryptographic     |          | verification |        |                      |           |                |                 |                      |              |                 |     |
| ------------- | ---------- | ----------- | -------- | ----------------- | -------- | ------------ | ------ | -------------------- | --------- | -------------- | --------------- | -------------------- | ------------ | --------------- | --- |
|               |            |             |          |                   |          |              |        | [12] J. Nie,         | J. Jiang, | Y. Li,         | and S.          | Ercisli, “Generative |              | ai-enhanced     | au- |
|               |            |             |          |                   |          |              |        | tonomous             | driving:  | Innovating     | decision-making |                      | and          | risk assessment |     |
| and dynamic   | behavioral |             | analysis | in AV ecosystems. |          | By           | fusing |                      |           |                |                 |                      |              |                 |     |
|               |            |             |          |                   |          |              |        | in multi-interactive |           | environments,” |                 | IEEE                 | Transactions | on Intelligent  |     |
| cryptographic | provenance |             | and      | reputation        | modeling | with         | a      |                      |           |                |                 |                      |              |                 |     |
TransportationSystems,2025.
dual-stage AI reasoning assistant, we provide a zero-trust [13] H.YanandY.Li,“Generativeaiforintelligenttransportationsystems:
ingestionlayerthatsecuresdecentralizedV2V,P2P,andinfras- Roadtransportationperspective,”ACMComputingSurveys,2025.
[14] M.Andreoni,W.T.Lunardi,G.Lawton,andS.Thakkar,“Enhancing
tructure feeds. Our evaluation demonstrates that this hybrid autonomous system security and resilience with generative ai: A
approachovercomesthefundamentalavailabilitylimitationsof comprehensive survey,” IEEE Access, vol. 12, pp. 109470–109493,
| traditional | methods, | while | cryptographic |     | baselines | effectively |     | 2024. |     |     |     |     |     |     |     |
| ----------- | -------- | ----- | ------------- | --- | --------- | ----------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
[15] V.Sanh,L.Debut,J.Chaumond,andT.Wolf,“Distilbert,adistilled
becomenon-functionalduetohighfalse-positiverates,whereas
|     |     |     |     |     |     |     |     | version | of bert: | smaller, | faster, | cheaper and | lighter,” | 2020. [Online]. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | -------- | -------- | ------- | ----------- | --------- | --------------- | --- |
our proposed AI-based fusion model maintains high accuracy Available:https://arxiv.org/abs/1910.01108
|          |              |     |            |       |      |     |        | [16] ISO, | “Information | technology | artificial | intelligence |     | — management |     |
| -------- | ------------ | --- | ---------- | ----- | ---- | --- | ------ | --------- | ------------ | ---------- | ---------- | ------------ | --- | ------------ | --- |
| (89.55%) | and superior |     | diagnostic | power | (AUC | =   | 0.937) |           |              |            |            |              |     |              |     |
system,”[online].available:https://www.iso.org/standard/42001.”
| within strict | on-vehicle |     | latency | budgets. | While | limitations |     |     |     |     |     |     |     |     |     |
| ------------- | ---------- | --- | ------- | -------- | ----- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[17] N.I.ChowdhuryandR.Hasan,“Howtrustworthyareover-the-air(ota)
regarding adaptive adversaries and distribution shifts remain, updatesforautonomousvehicles(av)toensurepublicsafety?:Athreat
model-basedsecurityanalysis,”in2024IEEEWorldForumonPublic
| our findings | move | the | field beyond | proof-of-concept |     | toward |     |     |     |     |     |     |     |     |     |
| ------------ | ---- | --- | ------------ | ---------------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
SafetyTechnology(WF-PST),pp.87–92.
| an operationally |     | grounded | architecture. |     | Future | research | will |                   |     |              |     |             |              |         |     |
| ---------------- | --- | -------- | ------------- | --- | ------ | -------- | ---- | ----------------- | --- | ------------ | --- | ----------- | ------------ | ------- | --- |
|                  |     |          |               |     |        |          |      | [18] G. Kueppers, |     | J.-P. Busch, | L.  | Reiher, and | L. Eckstein, | “V2aix: | A   |
focus on formal robustness analysis and privacy-preserving multi-modalreal-worlddatasetofetsiitsv2xmessagesinpublicroad
reputationaggregation,aimingtostandardizethesehybridtrust traffic,”inProc.2024IEEE27thInternationalConferenceonIntelligent
TransportationSystems(ITSC),2024,pp.392–398.
models for large-scale, safety-critical fleet deployments. [19] M. Chowdhury, A. Gawande, and L. Wang, “Secure information
|     |     |     |     |     |     |     |     | sharing | among | autonomous | vehicles | in ndn,” | in Proceedings |     | of the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ----- | ---------- | -------- | -------- | -------------- | --- | ------ |
ACKNOWLEDGEMENT
|     |     |     |     |     |     |     |     | Second | International | Conference |     | on Internet-of-Things |     | Design | and |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------------- | ---------- | --- | --------------------- | --- | ------ | --- |
Implementation,2017,pp.15–25.
ThisworkissupportedbytheDepartmentofEnergy(DOE)
[20] G.Rathee,A.Sharma,R.Iqbal,M.Aloqaily,N.Jaglan,andR.Kumar,“A
(Award#DE-CR0000046).Anyopinions,findings,conclusions,
blockchainframeworkforsecuringconnectedandautonomousvehicles,”
Sensors,vol.19,no.14,p.3165,2019.
| or recommendations |     | expressed |     | in this | material | are those | of  |     |     |     |     |     |     |     |     |
| ------------------ | --- | --------- | --- | ------- | -------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[21] K.Maeng,W.Kim,andY.Cho,“Consumers’attitudestowardinfor-
| the authors | and | do not | necessarily | reflect | the DOE’s | views. |     |        |          |         |         |           |                |            |     |
| ----------- | --- | ------ | ----------- | ------- | --------- | ------ | --- | ------ | -------- | ------- | ------- | --------- | -------------- | ---------- | --- |
|             |     |        |             |         |           |        |     | mation | security | threats | against | connected | and autonomous | vehicles,” |     |
TelematicsandInformatics,vol.63,p.101646,2021.
REFERENCES
[22] D.Parekh,N.Poddar,A.Rajpurkar,M.Chahal,N.Kumar,G.P.Joshi,
[1] G.Bathla,K.Bhadane,R.K.Singh,R.Kumar,R.Aluvalu,R.Krishna- andW.Cho,“Areviewonautonomousvehicles:Progress,methodsand
challenges,”Electronics,vol.11,no.14,p.2162,2022.
murthi,A.Kumar,R.Thakur,andS.Basheer,“Autonomousvehicles
[23] J.Sun,J.Tao,H.Zhang,Y.Zhao,L.Nie,X.Cheng,andT.Zhang,
andintelligentautomation:Applications,challenges,andopportunities,”
MobileInformationSystems,vol.2022,no.1,p.7632892,2022. “Atamper-resistantbroadcastingschemeforsecurecommunicationin
[2] T.M.N.VamsiandL.Pratibha,“Learningprocessesfortheinternetof internet of autonomous vehicles,” IEEE Transactions on Intelligent
TransportationSystems,vol.25,no.3,pp.2837–2846,2023.
autonomousvehiclesandintelligenttransportationsystems,”inWireless
Ad-hocandSensorNetworks. CRCPress,pp.87–111. [24] F.Gonc¸alves,B.Ribeiro,V.Hapanchak,S.Barros,O.Gama,P.Arau´jo,
[3] A.Giannaros,A.Karras,L.Theodorakopoulos,C.Karras,P.Kranias, M.J.Nicolau,B.Dias,J.Macedo,A.Costaetal.,“Securemanagement
ofautonomousvehicleplatooning,”inProceedingsofthe14thACM
| N. Schizas, | G.  | Kalogeratos, | and | D. Tsolis, | “Autonomous | vehicles: |     |     |     |     |     |     |     |     |     |
| ----------- | --- | ------------ | --- | ---------- | ----------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
InternationalSymposiumonQoSandSecurityforWirelessandMobile
Sophisticatedattacks,safetyissues,challenges,opentopics,blockchain,
| and | future directions,” |     | Journal | of Cybersecurity | and | Privacy, | vol. 3, | Networks,2018,pp.15–22. |     |     |     |     |     |     |     |
| --- | ------------------- | --- | ------- | ---------------- | --- | -------- | ------- | ----------------------- | --- | --- | --- | --- | --- | --- | --- |
[25] T.PradhanandP.Patil,“Quantumcryptographyforsecureautonomous
no.3,pp.493–543,2023.
|     |     |     |     |     |     |     |     | vehicle | networks: | A review,” | in  | 2024 IEEE | International | Students’ |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --------- | ---------- | --- | --------- | ------------- | --------- | --- |
[4] S.Gupta,C.Maple,andR.Passerone,“Aninvestigationofcyber-attacks
andsecuritymechanismsforconnectedandautonomousvehicles,”IEEE ConferenceonElectrical,ElectronicsandComputerScience(SCEECS).
IEEE,2024,pp.1–10.
Access,vol.11,pp.90641–90669,2023.
[26] T.Alam,“Dataprivacyandsecurityinautonomousconnectedvehicles
[5] A.Nepal,R.Doss,andF.Jiang,“Securedataprovenanceininternetof
vehicleswithverifiablecredentialsforsecurityandprivacy,”in202454th insmartcityenvironment,”BigDataandCognitiveComputing,vol.8,
no.9,p.95,2024.
AnnualIEEE/IFIPInternationalConferenceonDependableSystemsand
[27] J.Raiyn,“Dataandcybersecurityinautonomousvehiclenetworks,”
| Networks-SupplementalVolume(DSN-S). |     |     |     | IEEE,2024,pp.59–61. |     |     |     |     |     |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[6] ISO, “Road vehicles functional safety, [online]. avail- TransportandTelecommunication,vol.19,no.4,pp.325–334,2018.
able:https://www.iso.org/standard/68383.html.” [28] G. Bendiab, A. Hameurlaine, G. Germanos, N. Kolokotronis, and
S.Shiaeles,“Autonomousvehiclessecurity:Challengesandsolutions
[7] I.21434,“Roadvehicles—cybersecurityengineering,[online].avail-
able:https://www.iso.org/standard/70918.html.” using blockchain and artificial intelligence,” IEEE Transactions on
[8] C.Zhao,X.Dai,Y.Lv,J.Niu,andY.Lin,“Decentralizedautonomous IntelligentTransportationSystems,vol.24,no.4,pp.3614–3637,2023.
|     |     |     |     |     |     |     |     | [29] M. A. | Khan, | A. Alasiry, | M.  | Marzougui, | I. Bayhan, | S. S. | Kuna, |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ----- | ----------- | --- | ---------- | ---------- | ----- | ----- |
operationsandorganizationsintransverse:Federatedintelligencefor
smartmobility,”IEEETransactionsonSystems,Man,andCybernetics: G.S.N.Rao,S.A.Algamdi,andH.Aldossary,“Securingintelligent
Systems,vol.53,no.4,pp.2062–2072,2022. transportationsystems:Adual-frameworkapproachforprivacyprotection
andcybersecurityusinggenerativeai,”IEEETransactionsonIntelligent
| [9] I. Yaqoob, | L.  | U. Khan, | S. A. | Kazmi, M. | Imran, | N. Guizani, | and |     |     |     |     |     |     |     |     |
| -------------- | --- | -------- | ----- | --------- | ------ | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
TransportationSystems,2025.
C.S.Hong,“Autonomousdrivingcarsinsmartcities:Recentadvances,
requirements,andchallenges,”IEEENetwork,vol.34,no.1,pp.174– [30] R. H. Ahmed, M. Hussain, H. Abbas, S. Zahid, and M. H. Tariq,
|     |     |     |     |     |     |     |     | “Enhancing | autonomous |     | vehicle | security | through | advanced artificial |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---------- | --- | ------- | -------- | ------- | ------------------- | --- |
181,2019.
intelligencetechniques,”JournalofComputerScienceandElectrical
[10] P.Adekola,“Cryptographicsafeguardsandkeymanagementinautomo-
tivecommunicationnetworks:Securingdataintegrityandconfidentiality Engineering,vol.6,no.4,pp.1–6,2024.
|     |     |     |     |     |     |     |     | [31] S. Guntuka |     | and E. Shakshuki, |     | “Application | of generative | artificial |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ----------------- | --- | ------------ | ------------- | ---------- | --- |
inthecan,lin,andethernetecosystems,”2025.
intelligenceinminimizingcyberattacksonvehicularnetworks,”Procedia
ComputerScience,vol.251,pp.140–149,2024.
2932
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:34:02 UTC from IEEE Xplore.  Restrictions apply.