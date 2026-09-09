|     |     | FocalComm: |     |               | Hard Instance-Aware |                        |     | Multi-Agent |     | Perception |     |     |     |
| --- | --- | ---------- | --- | ------------- | ------------------- | ---------------------- | --- | ----------- | --- | ---------- | --- | --- | --- |
|     |     |            |     | DerejeShenkut |                     | VijayakumarBhagavatula |     |             |     |            |     |     |     |
CarnegieMellonUniversity
|     |     |     |     |     | {dshenkut, | vk16}@andrew.cmu.edu |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | ---------- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
Abstract Multi-agent1 CP where vehicles and infrastructure share
5202 ceD 02  ]VC.sc[  2v28931.2152:viXra
|     |     |     |     |     |     |     | complementary |     | perception | data | through | V2X communica- |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ---------- | ---- | ------- | -------------- | --- |
Multi-agent collaborative perception (CP) is a promis- tion has shown promise to address this. CP enables con-
ing paradigm for improving autonomous driving safety, nectedautonomousvehicles(CAVs)andinfrastructureunits
particularlyforvulnerableroaduserslikepedestrians,via to exchange visual perception information and scene rep-
robust 3D perception. However, existing CP approaches resentations from multiple viewpoints, mitigating single-
often optimize for vehicle detection performance metrics, agent perception limitations and improving detection reli-
underperformingonsmaller,safety-criticalobjectssuchas abilityforsafety-criticalscenarios.
| pedestrians, | where | detection | failures |     | can be catastrophic. |     |     |                                            |     |     |     |     |         |
| ------------ | ----- | --------- | -------- | --- | -------------------- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | ------- |
|              |       |           |          |     |                      |     |     | Collaborationcanbeatrawlevel(earlyfusion), |     |     |     |     | feature |
Furthermore, previous CP methods rely on full feature ex- level (intermediate fusion), or decision level (late fusion),
change rather than communicating only salient features basedonthedatasharingstage[11].Earlyfusionexchanges
that help reduce false negatives. To this end, we present unprocessedsensordata(images,LiDARpointclouds),re-
FocalComm, a novel collaborative perception framework quiring high communication bandwidth but enabling com-
thatfocusesonexchanginghard-instance-orientedfeatures
prehensivejointprocessing.Latefusiontransmitsonlyfinal
among connected collaborative agents. FocalComm con- detectionoutputs(e.g.,boundingboxes),minimizingband-
sists of two key novel designs, (1) a learnable progres- width needs but potentially introducing delays and infor-
| sive hard | instance | mining | (HIM) | module | to extract | hard |             |     |                                          |     |     |     |     |
| --------- | -------- | ------ | ----- | ------ | ---------- | ---- | ----------- | --- | ---------------------------------------- | --- | --- | --- | --- |
|           |          |        |       |        |            |      | mationloss. |     | Intermediatefusionstrikesabalancebyshar- |     |     |     |     |
instances-oriented features per agent, and (2) a query- ingcompressedfeaturerepresentations,offeringapractical
basedfeature-level(intermediate)fusiontechniquethatdy- compromise between communication efficiency and per-
namically weights these identified features during collab- ceptionperformance.Currentresearchhasexploredvarious
oration. We show that FocalComm outperforms state-of- aspectsofCP,includingbandwidthoptimizationandselec-
| the-art collaborative |     | perception |     | methods | on two | challeng- |     |     |     |     |     |     |     |
| --------------------- | --- | ---------- | --- | ------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- |
tiveinformationtransmission.WorkssuchasWhere2comm
ing real world datasets (V2X-Real and DAIR-V2X) across [12] have focused on optimizing bandwidth usage by se-
both vehicle-centric and infrastructure-centric collabora- lectivelytransmittinginformativefeatures,whileotherslike
tive setups. FocalComm also shows strong performance V2X-ViT[35]haveaddressedchallengessuchasnoisylo-
gaininpedestriandetectioninV2X-Real. Codeandmodel calization. Recent advances like SyncNet [17] have made
| checkpoints | are | available | at https://github.com/ |     |     |     |     |     |     |     |     |     |     |
| ----------- | --- | --------- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
progressinlatency-awarecollaboration,whileMPDA[34]
scdrand23/FocalComm. and DI-V2X [33] have tackled domain gap in multi-agent
collaboration.
Thedetectionofvulnerableroaduserssuchaspedestri-
1.Introduction ans remains understudied in CP settings, both in terms of
|     |     |     |     |     |     |     | available | datasets | and | methodological |     | approaches. | While |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------- | --- | -------------- | --- | ----------- | ----- |
Theabilitytoperceiveandinterpretthesurroundingsac-
|     |     |     |     |     |     |     | current | CP  | systems achieve | good | performance |     | on vehicle |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- | --------------- | ---- | ----------- | --- | ---------- |
curatelyisatthecoreofthepromiseofautonomousvehicle
detection,theysignificantlyunderperformonpedestriande-
| (AV) systems. |     | Research | in AVs | [2,10,28] | has made | sig- |     |     |     |     |     |     |     |
| ------------- | --- | -------- | ------ | --------- | -------- | ---- | --- | --- | --- | --- | --- | --- | --- |
tection. Thisperformancegapisofmuchconcernaspedes-
nificantprogress,withthepotentialforafutureofsaferand
triandetectionposesuniquechallengesduetotheirsmaller
moreefficientintelligenttransportationsystems.Atthecore
|                                     |     |     |     |     |                     |     | size, | occlusions, | and      | weak sensing | from       | long ranges, | yet     |
| ----------------------------------- | --- | --- | --- | --- | ------------------- | --- | ----- | ----------- | -------- | ------------ | ---------- | ------------ | ------- |
| ofthisprogressliesrobustperception. |     |     |     |     | Whilesingle-vehicle |     |       |             |          |              |            |              |         |
|                                     |     |     |     |     |                     |     | they  | represent   | critical | safety       | risks when | missed       | (nearly |
perceptionhasadvancedsignificantlythroughmulti-sensor
fusion(cameras,LiDAR,radar)anddataintensivelearning-
1Anagentreferstoeitheravehicleorinfrastructureunitwithbothper-
basedtechniques,itremainsconstrainedbylimitedfield-of-
|     |     |     |     |     |     |     | ceptioncapability(e.g. |     | LiDAR)andV2Xcommunicationmodulesthat |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | ------------------------------------ | --- | --- | --- | --- |
view,occlusions,anddegradedperformanceatlongranges. enableittoshareandreceiveinformation.

7,522 pedestrian deaths in the USA in 2022 alone [22]). fusiontoachieveefficientCP,withparticularbenefits
Therefore,thereisapressingneedforCPsystemsthatcan forhard-to-detectobjectslikepedestrians.
effectively handle multi-class detection scenarios, particu-
2.RelatedWork
larlyforsafety-criticalclasseslikepedestrians.
To address this challenge, we draw inspiration from a
CollaborativePerception Collaborativeperception(CP)
well-established line of work in single-agent perception:
via vehicle-to-everything (V2X) communications presents
hardinstancemining. Thesetechniques,whichidentifyand
a promising approach to enhance autonomous vehicles’
prioritizedifficult-to-detectobjectsthroughloss-basedsam-
ability to perceive through occlusions and extend long-
pling [26] or adaptive weighting [6,19,31], have shown
range detection capabilities [35]. V2VNet [30] presents
significant promise. They have proven particularly effec-
anintermediate-levelfusionapproachwherevehiclescom-
tiveatimprovingdetectionperformanceonchallengingob-
press and exchange intermediate network representations
jects by giving more focus on the most difficult examples
throughagraphneuralnetwork. DiscoNet[18]implements
duringtraining, withrecentworkslikeFocalFormer3D[6]
a knowledge distillation-based fusion method, while Att-
andHINTED[31]demonstratingstrongresultsongeneral
Fuse[36]developsanattention-basedV2Vframeworkand
3Ddetectiontasks. Theseapproacheshaveledtoimprove-
introducedtheOPV2Vbenchmark. Addressingcommuni-
mentsindetectingdifficultinstancessuchassmallobjects,
cationconstraintsiscrucialforpracticaldeploymentofCP
partiallyoccludedtargets,andobjectsatlongrange. Moti-
systems[25]. V2X-ViT[35]introducedvisiontransformer-
vatedbytheseadvances, weobservethathardinstancefo-
basedcollaborationrobusttonoisylocalization,while[17]
cused collaboration could significantly benefit multi-agent
addressed latency-aware collaboration through temporal
perception by addressing communication constraints and
alignment. Bandwidth optimization has been explored
detection challenges simultaneously. Adapting these tech-
via spatial confidence maps [12], codebook compression
niquesto CPrequires carefularchitectural designto effec-
[13], multi-resolution fusion [29], pragmatic communica-
tively prioritize difficult instances across multiple agents
tion [38], and vector quantization [24]. Recent works ad-
withbandwidthconstraints.
dressheterogeneousagentcollaboration[20,33,34],robust-
In this paper, we introduce FocalComm, a novel multi-
ness to pose errors [21], sim2real adaptation [16], end-to-
agentCPmethodthatprioritizeshardinstance-orientedfea-
end driving [7], and unsupervised learning [5]. Further
turesbasedonalearnabledifficulty-awareinstanceidentifi-
advances include latency-aware alignment [27], sparse fu-
cationapproach.Ourapproachconsistsofastage-wisehard
sion[41],andmulti-modaldatasetswith4DRadar[39].
instanceidentificationmodulefollowedbyadaptivefeature
fusion module that selectively combines information from
Hard Instance-Aware Detection Detecting challenging
multiple agents based on instance-level difficulty queries.
objectsaccuratelyiscrucialforreliableperceptionsystems,
Our approach is motivated by the observation that not all
particularly in safety-critical applications like autonomous
objects require equal collaborative effort. While vehicles
driving. Earlyapproachestohardexamplemininginclude
are often detected reliably by a single agent, pedestrians
OnlineHardExampleMining(OHEM)[26],whichdynam-
and smaller objects benefit more from multi-agent collab-
ically selects the most difficult examples during training
orationduetotheirsizeandlikelihoodofocclusion. Byfo-
by computing losses for all region proposals and select-
cusingexchanginginformationaboutthesechallengingin-
ing those with highest losses, while using non-maximum
stances,FocalCommachievessuperiorperformanceonthe
suppression to prevent redundant regions from dominat-
realmulti-classmulti-agentcollaborativeperceptionbench-
ing. Focal loss [19] takes a different approach by auto-
mark [32]. Our contributions in this paper can be summa-
matically down-weighting easy examples through a modi-
rizedasfollows.
fiedcross-entropyloss,addressingtheextremeforeground-
1. We develop a multi-stage hard instance mining tech- backgroundclassimbalance.Morerecentmethodshaveex-
nique that extracts features ranked with detection un- plored specialized techniques for identifying and handling
certainty across multiple object classes from each difficult samples. IoU-aware sampling [23] balances easy
agent to progressively focus on increasingly difficult and hard examples based on their intersection over union
detectioncases. (IoU) distributions, while Cascade R-CNN [3] employs a
sequenceofdetectorswithincreasingIoUthresholdstopro-
2. Weproposeaquery-guidedmulti-agentfeatureaggre-
gressively handle more difficult instances. In the 3D de-
gation strategy that prioritizes hard instance-oriented
tection domain, researchers have developed various strate-
queriesacrosscollaborativeagentswhiledynamically
gies to address challenging detection scenarios. SST [8]
weightingoffeaturesandqueriesfromeachagent.
leveragesattentionmechanismsthatpreservespatialinfor-
3. WepresentFocalComm,anend-to-endframeworkthat mation for small objects, while FSD [9] focuses on iden-
integrates difficulty-aware mining and query-guided tifying objects in sparse, long-range contexts. Recent ad-

SharedFeatureEncoding HardInstanceMiningModule Query-guidedFusion&Detection
M
DetectionHeads
|     |     |     | E   | ⊥P  |     |     |
| --- | --- | --- | --- | --- | --- | --- |
Hs
e
|     | Ego(X ) |     | F   |     |     |     |
| --- | ------- | --- | --- | --- | --- | --- |
|     | e       |     | e   |     |     |     |
M
Q
|     |     |     | E   | ⊥P  | QAFF |     |
| --- | --- | --- | --- | --- | ---- | --- |
Hs
i
F i
| CAV(X | )   |     |     |     |       |     |
| ----- | --- | --- | --- | --- | ----- | --- |
|       | i   |     | M   |     |       |     |
|       |     |     |     |     | K V E | C   |
Encoder(Φ)
E
|     |     |     |     | ⊥P  | Encoder | Concat. |
| --- | --- | --- | --- | --- | ------- | ------- |
Hs
j
F
|     |     |     | j   |     | ⊥P  | M   |
| --- | --- | --- | --- | --- | --- | --- |
C
| Infra(X | )   |     |     |     |         |      |
| ------- | --- | --- | --- | --- | ------- | ---- |
|         | j   |     |     |     | Project | Mask |
F
BEV
Figure1.TheoverallarchitectureofFocalCommwiththreekeycomponents:(1)parallelfeatureextractionthroughasparse3Dbackbone
networkandencodingviavoxelfeatureencoder(Φ),(2)progressiveHardInstanceMining(HIM)forfeature-levelidentificationofhard
to detect objects across stages, and (3) Query-guided Adaptive Feature Fusion (QAFF) for aggregating multi-agent features based on
instance-levelqueries.
vances have specifically targeted hard instance mining for includingtheegovehicle,otherconnectedautonomousve-
3Ddetection. FocalFormer3D[6]introducesamulti-stage hicles (CAVs), and infrastructure sensors. Each agent’s
HardInstanceProbing(HIP)mechanismthatidentifiespo- point cloud data (X for ego, X for the other CAVs, and
e i
tential false negatives through progressive refinement by X for infrastructure) is first processed through identical
j
maintainingclass-awareaccumulatedpositivemaskstofo- sparse voxel feature encoders (denoted as Φ), producing
cus training on increasingly difficult instances while omit- agent-specificfeaturemaps(F e ,F i ,F j ). Thesefeaturesare
tingeasypositives. HINTED[31]addresseshardinstances thenprocessedthroughtwokeycomponents: (1)aprogres-
insparsely-supervisedsettingsbycombiningmixed-density sive Hard Instance Mining (HIM) module that generates
(Hs, Hs, Hs)
feature fusion. Most recently, BEVFusion-DHIP [14] ex- stage-wise heatmaps and suppresses easy
e i j
tendshardinstanceminingtomulti-modalfusionbyapply- samplesusingmask(M)tofocusonmorechallengingob-
ingdualHIPtobothLiDARBEVfeaturesand3Dposition- jectsacrossmultiplestages,and(2)Query-guidedAdaptive
aware image features, systematically reducing false nega- Feature Fusion (QAFF) that aggregates the instance-aware
tives crucial for autonomous driving safety. Despite these queriesfromallagentsintoaunifiedrepresentation,which
advances in single-agent perception, hard instance mining is combined with concatenated BEV features (F BEV ) be-
incollaborativeperceptionscenariosremainslargelyunex- forefeedingintothedetectionhead.
| plored. | Our work, FocalComm, | addresses | this gap by de- |     |     |     |
| ------- | -------------------- | --------- | --------------- | --- | --- | --- |
velopingaprogressivehardinstanceminingtechniquetai-
loredspecificallyformulti-agentCPscenarios,wherechal- FeatureExtraction Eachagentprocessesitspointcloud
datathroughasharedsparsevoxelfeatureencoderΦ,pro-
lengingobjectscanbebetteridentifiedandhandledthrough
collaborativeinformationexchange. ducingagent-specificfeaturemaps:
|                      |     |     |     | F =Φ(X )∈RH×W×C, | k ∈{e,i,j} | (1) |
| -------------------- | --- | --- | --- | ---------------- | ---------- | --- |
| 3.FocalCommFramework |     |     |     | k k              |            |     |
Our proposed FocalComm architecture is illustrated in whereX representspointcloudinputsfromego,CAV,and
k
Fig. 1. FocalComm processes inputs from multiple agents infrastructureagents.

Algorithm1HardInstanceMining(HIM) Algorithm 2 Query-guided Adaptive Feature Fusion
(QAFF)
Require: Multi-agentfeaturesF,GTboxesG,stagesS
1: F orig ←F ▷Cache Require: Query features {Qi s }n s= S 1 from each agent i,
2: M acc ←0 ▷Initialize Agent features F i ∈ RC×H×W, Valid agent mask
3: fors∈{1,...,n S }do M∈{0,1}N
4: M spatial ←max(M acc ) ▷Flatten 1: fors∈{1,...,n S }do
5: F masked ←F orig ⊙(1−M spatial ) ▷Mask 2: Q˜ s ←MHSA({Qi s } i ,M) ▷Cross-agentattention
6: Fˆ s ←Ψ s (F masked ) ▷Extract 3: endfor
7: P s ←Ω(Fˆ s ) ▷Detect 4: ω s ←softmax(SA(Q˜ s )) ▷Stageimportanceweights
8: iftrainingthen
9: T s ←Match(P s ,G) ▷Assign 5: Q¯ ← (cid:80)S s=1 ω s Q˜ s ▷Stage-wisefeatureaggregation
10: else 6: K,V←Proj({F i } i ) ▷Projectfeaturestokey-value
11: T s ←Filter(P s ) ▷Threshold 7: F cross ←MHCA(Q¯,K,V,M) ▷Query-guidance
12: endif 8: α i ←softmax(AA(F cross )⊙M) ▷Agentweights
13: M acc ←max(M acc ,T s ) ▷Update 9: F out ← (cid:80) i α i F c i ross ▷Weightedfeaturefusion
14: endfor Ensure: FusedfeaturesF out ∈RC×H×W
15: Q←Combine({Fˆ s }) ▷Fuse
Ensure: QueryfeaturesQ,Predictions{P },Masks{T }
s s
s, QAFF first performs multi-head self-attention (MHSA)
acrossagentstogeneratestage-specificrepresentationsQ˜ .
s
3.0.1 HardInstanceMining(HIM) Thiscross-agentattentionmechanismallowsagentstocol-
laborativelyrefinetheirunderstandingofobjectsateachdif-
A key part of FocalComm is the Hard Instance Min- ficultylevelwhileaccountingforpotentiallymissingorin-
ing (HIM) module that extracts hard instance identifying active agents through the mask M. The stage-wise repre-
features in a multi-stage manner. Each stage focuses on sentations are then combined through learned importance
increasingly difficult instances while avoiding redundant weights ω , computed via a stage attention (SA) mecha-
s
attention to already-identified objects through mask accu- nism and softmax normalization. This adaptive weight-
mulation. As detailed in Algorithm 1, HIM processes ing scheme produces a unified query representation Q¯ =
features through n S progressive stages. The key inno- (cid:80)S s=1 ω s Q˜ s that emphasizes the most informative stages
vation lies in the progressive masking: at each stage s, basedonthecurrentscenecontext. Theoriginalagentfea-
the accumulated mask M acc suppresses detected regions tures{F i } i areprojectedintokey-valuespacetoobtainK
throughF masked = F orig ⊙(1−M spatial ),forcingsub- andV. Multi-headcross-attention(MHCA)isthenapplied
sequent stages to focus on harder instances. The Match() between the unified queries Q¯ and these key-value pairs,
and Filter() functions handle mask generation differently producing F that captures comprehensive multi-agent
cross
for training and inference. During training, Match(P s ,G) understanding. Finally, agent-specificattentionweightsα i
performs Hungarian assignment between predictions and arecomputedthroughanagentattention(AA)mechanism,
groundtruth,returningbinarymasksatlocationswhereIoU takingintoaccountthevalidagentmaskM. Theseweights
exceeds τ iou . During inference, Filter(P s ) applies confi- determineeachagent’scontributiontothefinalfusedoutput
dencethresholding: T s = 1[σ(H s ) > τ ·γs],whereH s is F out = (cid:80) i α i F c i ross ,emphasizingagentswithmoreinfor-
thedenseheatmap,τ isthebasethreshold,andγisadecay mative observations. These weights automatically empha-
factor controlling stage-wise threshold progression. Each sizeagentswithmorereliableorinformativeobservations,
stageproducesfeaturesFˆ s concatenatedtoformqueryfea- accounting for variations in viewpoint quality and sensing
turesQ∈RN×(nS·C)×H×W.
capabilities. TheoutputofQAFFisthenpassedtothede-
tectiondecoders(showninpurpleinFig.1)forfinalobject
detectionandclassification.
3.0.2 Query-guidedAdaptiveFeatureFusion(QAFF)
3.1.DetectionDecoderandJointOptimization
The Query-guided Adaptive Feature Fusion (QAFF)
module takes instance-aware queries from HIM to aggre- The final fused features, F , are passed to the de-
Fuse
gateinformationacrossmultipleagents. AsshowninAlgo- tection head. Different from previous multi-agent collab-
rithm2,QAFFtakesasinputthestage-wisequeryfeatures orative perception works, we adopt an anchor-free detec-
{Qi}S from each agent i, along with their original fea- tion head [1] that supervises the regression and classifica-
s s=1
turesF ∈RC×H×W andavalidagentmaskM∈{0,1}N tion tasks as well as allows joint optimization of the mul-
i
indicating participating agents in the scene. For stage tistage hard instance identification. This anchor-free ap-

proach eliminates the need for complex predefined anchor multi-class(vehicle,pedestrian,andtruck)annotationand
designsandprovidesmoredirectobjectlocalization,which itallowsvehicle-centricandinfrastructure-centricCPeval-
is particularly beneficial for detecting hard instances with uation. We use the train/val/test split with 23379, 2770,
unusualscalesorocclusionpatternsthattraditionalanchor- and 6850 frames respectively as proposed in the bench-
| based | methods | might struggle | with. | Furthermore, |     | our ap- | mark[32]. |     |     |     |     |     |
| ----- | ------- | -------------- | ----- | ------------ | --- | ------- | --------- | --- | --- | --- | --- | --- |
proachnaturallyhandlesmulti-classdetectionscenarios,ef-
| fectively | identifying | various | road | users | including | pedestri- |          |          |         |           |             |       |
| --------- | ----------- | ------- | ---- | ----- | --------- | --------- | -------- | -------- | ------- | --------- | ----------- | ----- |
|           |             |         |      |       |           |           | DAIR-V2X | DAIR-V2X | [40] is | the first | large-scale | real- |
ans, which exhibit significant variation in size and appear- worlddatasetforVehicle-Infrastructurecooperativepercep-
ance. Our detection head consists of a transformer de- tion.Thedatasetcomprises71KLiDARandcameraframes
| coder | based on | [1] that | processes | feature | queries | from a |     |     |     |     |     |     |
| ----- | -------- | -------- | --------- | ------- | ------- | ------ | --- | --- | --- | --- | --- | --- |
collectedfromrealscenarioswithcomprehensive3Danno-
dense heatmap prediction branch. The detection tasks are tations. Itfeaturesvehicle-infrastructurecollaborationwith
jointlyoptimizedwithhierarchicalinstanceminingthrough
temporalasynchronychallengesandincludesV2X-Seqex-
amulti-componentlossfunction: tensionwith15Kframesforsequentialperceptionandtra-
jectoryforecastingtasks.
S
(cid:88)
| L=λ | L     | +λ L   | +λ L | +λ  |     | Ls      |                |          |        |           |     |             |
| --- | ----- | ------ | ---- | --- | --- | ------- | -------------- | -------- | ------ | --------- | --- | ----------- |
|     | 1 cls | 2 bbox | 3    | hm  | 4   | him (2) |                |          |        |           |     |             |
|     |       |        |      |     | s=1 |         | Implementation | Details. | During | training, |     | we voxelize |
thepointcloudwithavoxelsizeof0.2m×0.2m×0.4m
| where      | L is            | the focal classification |         | loss,       | L    | is the L1     |               |                         |           |            |            |             |
| ---------- | --------------- | ------------------------ | ------- | ----------- | ---- | ------------- | ------------- | ----------------------- | --------- | ---------- | ---------- | ----------- |
|            | cls             |                          |         |             | bbox |               |               |                         |           |            |            |             |
|            |                 |                          |         |             |      |               | and use       | a range of [−100m,100m] |           | for        | the x      | and y axes, |
| regression | loss            | for bounding             | box     | parameters, |      | L hm is the   |               |                         |           |            |            |             |
|            |                 |                          |         |             |      |               | and [−10m,6m] | for the                 | z axis.   | Each voxel | aggregates | up          |
| Gaussian   | focal           | loss for heatmap         |         | prediction. |      | Ls repre-     |               |                         |           |            |            |             |
|            |                 |                          |         |             |      | him           | to 20 points. | We implement            | FocalComm |            | using      | PyTorch     |
| sents      | the progressive | loss                     | for the | multi-stage |      | hard instance |               |                         |           |            |            |             |
andtrainonfourH100GPUswithabatchsizeof8for50
| miningatstages. |     | Theweightsλ |     | ,λ ,λ | ,andλ | balance |     |     |     |     |     |     |
| --------------- | --- | ----------- | --- | ----- | ----- | ------- | --- | --- | --- | --- | --- | --- |
1 2 3 4 epochs with Adam [15] optimizer with learning rate start-
| thecontributionsofdifferentlosscomponents. |     |     |     |     |     | Thespecific |        |              |          |       |     |       |
| ------------------------------------------ | --- | --- | --- | --- | --- | ----------- | ------ | ------------ | -------- | ----- | --- | ----- |
|                                            |     |     |     |     |     |             | 1e−4   |              |          |       |     | 1e−2. |
|                                            |     |     |     |     |     |             | ing at | and applying | a weight | decay | of  | Our   |
valuesofthesehyperparametersareprovidedintheimple-
modelemploysastandardsparse3DCNNbackbonecom-
mentationdetailssection.
monlyusedinLiDAR-based3Ddetection,similartoVoxel-
4.Experiments Net[43]andSECOND[37]. Theprogressivehardinstance
|     |     |     |     |     |     |     | mining          | (HIM) module | employs | a multi-stage |     | architecture |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ------------ | ------- | ------------- | --- | ------------ |
|     |     |     |     |     |     |     | with confidence | thresholds   | of 0.4, | utilizing     | a   | pooling ker- |
WeevaluateFocalCommonV2XReal[32]andDAIR-
V2X [40] datasets. To the best of our knowledge, V2X- nel size of 3 for local detection peaks and masking with
Real is the only publicly accessible multi-agent collabora- an attention decay factor of 2.0 to progressively identify
tive real dataset with enough multiclass annotation includ- challenging instances. Our query-guided adaptive feature
ingpedestrians.Fortraining,werandomlyassignoneagent fusion (QAFF) module employs multi-head attention with
|     |     |     |     |     |     |     | 8 heads | and hidden dimension | of  | 256 to | dynamically | fuse |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------------------- | --- | ------ | ----------- | ---- |
astheegovehicle,whileatinferencetimeweusepredefined
ego agents based on the dataset’s categorization. Our ex- featuresacrossagentsbasedonqueryimportance. Thede-
periments evaluate performance under two configurations, tection head follows a TransFusion [1] head with separate
i.e.vehicle-centricandinfrastructure-centric,wheretheego prediction branches for center, height, dimension, and ro-
agent is vehicle and infrastructure, respectively. For a fair tation. Ourmulti-componentlossfunctionbalancesdetec-
comparison, all methods are implemented using the same tion and mining objectives with weights λ =1.0 for clas-
1
3D backbone [37] and anchor-free head [1]. We adopt a sification, λ 2 =2.0 for bounding box regression, λ 3 =1.0
voxel-based method and anchor-free detection head across for heatmap prediction, and λ =0.5 for the hard instance
4
allcomparedmodelstopushforimproveddetectionperfor- mining component per agent. These weights were deter-
manceforsmallerclassessuchaspedestrianswhileensur- mined through extensive ablation studies on the validation
ingfaircomparisonincollaborativeperception. set. Theweightsλ -λ followestablishedpracticesinprior
1 3
|     |     |     |     |     |     |     | detectionworks[1],whileλ |     | 4 wasspecificallytunedforour |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | ---------------------------- | --- | --- | --- |
4.1.Datasets
|           |          |     |         |               |     |            | approach    | to prevent overfitting |            | to difficult | examples | early    |
| --------- | -------- | --- | ------- | ------------- | --- | ---------- | ----------- | ---------------------- | ---------- | ------------ | -------- | -------- |
|           |          |     |         |               |     |            | in training | while still ensuring   | sufficient |              | gradient | flow for |
| V2X-Real. | V2X-Real |     | [32] is | a large-scale |     | real-world |             |                        |            |              |          |          |
dataset designed for V2X cooperative perception. It in- learningchallengingcases.Thisbalanceensuresstablecon-
vergencewhilemaintainingfocusonbothcommonandrare
| cludes | 33K LiDAR | frames | and over | 1.2 | million | annotated |     |     |     |     |     |     |
| ------ | --------- | ------ | -------- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- |
3Dboundingboxes. Thedatasetiscollectedusingtwocon- detectionscenarios.
| nected | automated | vehicles | and | two smart | infrastructures. |     |     |     |     |     |     |     |
| ------ | --------- | -------- | --- | --------- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
4.2.QuantitativeEvaluation
| The dataset | is  | collected in | two | scenarios: | V2X | smart in- |     |     |     |     |     |     |
| ----------- | --- | ------------ | --- | ---------- | --- | --------- | --- | --- | --- | --- | --- | --- |
tersections and V2V corridors. There are a maximum of Evaluation Protocol. Similar to the evaluation protocol
four agents in a scene. The V2X-Real dataset contains inV2VNet[30]andV2X-Real[32],ourevaluationisdone

|     |     |     |     |     |     | V2XReal(Kmax=4) |     |       |     |         | DAIR-V2X(Kmax=2) |         |     |
| --- | --- | --- | --- | --- | --- | --------------- | --- | ----- | --- | ------- | ---------------- | ------- | --- |
|     |     |     | Car |     |     | Pedestrian      |     | Truck |     | Overall |                  | Vehicle |     |
Method
|     |     | VC  |     | IC  | VC  |     | IC  | VC IC |     | VC  | IC  | VC  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 mAP@0.3/0.5 mAP@0.3/0.5 AP@0.3 AP@0.5
NoCollaboration 73.7/68.4 70.6/59.1 31.8/13.9 29.7/10.7 21.2/15.7 46.6/42.0 42.2/32.7 49.0/37.3 58.9 54.4
F-Cooper[4] 88.3/85.6 84.3/80.8 47.8/22.7 45.4/15.9 47.9/46.1 48.3/47.9 61.3/51.4 59.4/48.2 70.4 64.8
V2VNet[30] 87.0/84.4 85.0/81.4 34.5/13.9 36.5/15.2 40.0/36.8 44.3/41.9 53.8/45.0 55.3/46.2 69.5 63.5
Attfuse[34] 81.3/80.7 81.5/80.9 46.8/21.7 48.5/24.8 49.6/47.7 47.6/45.7 59.2/50.0 59.2/50.5 69.7 63.8
CoBEVT[12] 87.2/85.6 84.1/82.1 54.8/26.1 52.3/25.6 50.1/45.1 48.9/47.8 64.0/53.3 61.7/52.9 72.8 65.7
V2XViT[35] 83.9/81.1 81.4/78.2 38.5/15.2 33.5/13.3 42.5/35.6 45.4/38.9 55.0/44.0 53.4/43.5 74.5 67.6
CoAlign[21] 85.8/83.4 84.7/83.4 38.3/17.3 36.4/14.8 52.7/43.9 53.2/51.1 59.9/48.2 58.1/49.8 76.9 69.7
ERMVP[42] 88.5/86.4 86.7/84.0 53.2/25.4 50.6/23.5 42.9/41.3 41.7/38.7 61.5/51.0 59.7/48.7 69.2 63.4
FocalComm(ours) 91.5/89.6 86.2/84.8 57.4/27.3 51.2/26.7 53.9/51.6 49.6/47.3 67.6/56.1 62.3/52.9 77.2 70.1
Table1. PerformancecomparisononV2X-RealdatasetunderVehicle-Centric(VC)andInfrastructure-Centric(IC)collaborativesetups.
Results showAP@0.3/AP@0.5 format. Best results arein boldface. In no collaborationmode, VCmeans vehicle onlyand ICmeans
| infrastructureonly.K |     | max | isthemaximumnumberofagentsperscene. |     |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
intherangeof[−100m,100m]inboththex−axisandy− performs V2V: truck detection benefits most (+10.3%
axisofthechosenegoagent. Weadoptthestandardaver- AP@0.3,from50.5%to60.8%)duetoinfrastructure’sele-
ageprecision(AP)atintersection-over-union(IoU)thresh- vatedviewpointprovidingbettercoverageoflargeobjects,
oldof0.3and0.5foreachclassandmeanaverageprecision while pedestrian detection gains +4.6% (53.9% to 58.5%)
averagedoverallnumberofclasses. Followingestablished fromreducedocclusions.Vehicledetectionshowsasmaller
practices for datasets in V2X-Real with significant object gap(+1.3%)ascarsarewell-detectedfromeitherperspec-
size variations, we use these lower IoU thresholds to ac- tive. These results demonstrate our method’s ability to ef-
countforthechallengingnatureofdetectingobjectsranging fectively leverage the complementary viewpoints available
fromsmallpedestrianstolargevehiclesinCPscenarios. indifferentcollaborationscenarios.
4.3.QualitativeEvaluation
| Performance |     | Comparison. |     | Table | 1 presents | the | com- |     |     |     |     |     |     |
| ----------- | --- | ----------- | --- | ----- | ---------- | --- | ---- | --- | --- | --- | --- | --- | --- |
parison between our FocalComm and existing methods Detection Results. We visualize detection results from
|        |          |      |         |       |      |                 |     | both infrastructure-centric |     |     | (IC) and vehicle-centric |     | (VC) |
| ------ | -------- | ---- | ------- | ----- | ---- | --------------- | --- | --------------------------- | --- | --- | ------------------------ | --- | ---- |
| on the | V2X-Real | [32] | dataset | under | both | infrastructure- |     |                             |     |     |                          |     |      |
centric(IC)andvehicle-centric(VC)settings. Ourmethod perspectives across two scenes in Figure 2. Scene 1 (left)
andScene2(right)demonstratesourmethod’sperformance
| achieves | state-of-the-art |     | performance |     | across | all | metrics, |     |     |     |     |     |     |
| -------- | ---------------- | --- | ----------- | --- | ------ | --- | -------- | --- | --- | --- | --- | --- | --- |
atacomplexintersectionfrombird’s-eyeview.InScene1’s
| with significant |     | improvements. |     | In  | the vehicle-centric |     | set- |     |     |     |     |     |     |
| ---------------- | --- | ------------- | --- | --- | ------------------- | --- | ---- | --- | --- | --- | --- | --- | --- |
ting, FocalComm achieves 67.6% mAP@0.3 and 56.1% denseintersection,FocalCommaccuratelydetectscrowded
pedestriansandmostofthetrucks,wherepreviousmethods
| mAP@0.5, | representing |     | a   | 5.6% | and 5.1% | absolute | im- |     |     |     |     |     |     |
| -------- | ------------ | --- | --- | ---- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- |
provement over the next best method (CoBEVT). The often struggle with occlusions and object overlap. Scene
2highlightsourmethod’seffectivenessindetectingdistant
| performance | gains | are | particularly |     | pronounced | for | pedes- |         |              |        |          |         |           |
| ----------- | ----- | --- | ------------ | --- | ---------- | --- | ------ | ------- | ------------ | ------ | -------- | ------- | --------- |
|             |       |     |              |     |            |     |        | objects | and multiple | object | classes. | Through | effective |
triandetection,whereFocalCommachieves57.4%AP@0.3
and 27.3% AP@0.5 in the vehicle-centric setting, signifi- multi-agent collaboration, our method successfully detects
|                      |     |     |               |     |                |     |          | cars (shown | in red), | pedestrians | (shown | in orange), | and |
| -------------------- | --- | --- | ------------- | --- | -------------- | --- | -------- | ----------- | -------- | ----------- | ------ | ----------- | --- |
| cantly outperforming |     |     | all baselines |     | and addressing |     | a criti- |             |          |             |        |             |     |
cal safety need. Similarly, truck detection improves sub- trucks (shown in magenta) across varying distances. The
stantially from 21.2% to 53.9% AP@0.3, demonstrating methodparticularlyexcelsatmaintainingreliabledetection
|              |     |               |     |                |     |       |          | performance | for distant |     | objects and handling | cases | where |
| ------------ | --- | ------------- | --- | -------------- | --- | ----- | -------- | ----------- | ----------- | --- | -------------------- | ----- | ----- |
| our method’s |     | effectiveness |     | on challenging |     | large | objects. |             |             |     |                      |       |       |
For infrastructure-centric scenarios, our method maintains objectsareonlypartiallyvisible. Ourmethodachieveshigh
|          |             |     |          |         |         |         |        | precision   | with very    | few | false positives, | while maintaining |     |
| -------- | ----------- | --- | -------- | ------- | ------- | ------- | ------ | ----------- | ------------ | --- | ---------------- | ----------------- | --- |
| strong   | performance |     | with     | 62.3%   | mAP@0.3 | and     | 52.9%  |             |              |     |                  |                   |     |
|          |             |     |          |         |         |         |        | high recall | with minimal |     | false negatives, | as evidenced      | by  |
| mAP@0.5. | On          | the | DAIR-V2X | dataset | for     | vehicle | detec- |             |              |     |                  |                   |     |
tion, FocalComm achieves competitive results with 77.2% the close alignment between predicted boxes and ground
truthannotationsacrossbothscenes.
| AP@0.3and70.1%AP@0.5, |     |     |     | demonstratingstronggener- |     |     |     |     |     |     |     |     |     |
| --------------------- | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
alizationacrossdifferentV2Xscenarios.
Table 2 further validates our approach in specific com- QueryFeatures. Toprovideinsightsintoourmodel’sat-
munication scenarios. In V2V settings, FocalComm tentionmechanism,wevisualizethemeanofqueryfeatures
reaches 64.8% mAP@0.3, while in I2I configurations and their progression across the three stages of Hard In-
it achieves an impressive 70.2% mAP@0.3 and 58.1% stanceMining(HIM)inFigure3. Thevisualizationshows
mAP@0.5,outperformingallbaselinesbysubstantialmar- resultsfromtwodifferentagents,witheachrowrepresent-
gins. Analyzing per-class patterns, I2I consistently out- inganagent’sperspective.Thefirstthreecolumnsshowthe

Figure2. QualitativedetectionresultsofFocalComm,V2XViT[35],andF-Cooper[4]onV2X-Real(croppedto80×80maroundego).
GroundtruthandpredictionsareshownforCar(GT:darkgreen,Pred: red),Pedestrian(GT:cyan,Pred: orange),andTruck(GT:light
blue,Pred:magenta).
V2X-RealCommunicationScenarios
Vehicle Pedestrian Truck Overall
Method
V2V I2I V2V I2I V2V I2I V2V I2I
AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 AP@0.3/0.5 mAP@0.3/0.5 mAP@0.3/0.5
NoCollaboration 73.7/68.4 70.6/59.1 31.8/13.9 29.7/10.7 21.2/15.7 46.6/42.0 42.2/32.7 49.0/37.3
F-Cooper[4] 86.6/83.2 84.0/79.9 45.3/23.3 49.7/21.0 45.5/40.8 59.3/58.2 59.1/49.1 64.3/53.0
V2VNet[30] 86.5/82.5 86.7/82.1 31.1/13.1 41.9/18.9 39.2/32.9 53.5/49.8 52.3/42.8 60.7/50.3
AttFuse[34] 81.1/79.9 82.8/81.8 44.4/20.5 52.1/28.2 48.7/46.5 57.4/55.3 58.1/49.0 64.1/55.1
CoBEVT[12] 86.1/83.9 84.0/81.1 51.0/28.5 53.1/30.6 48.6/43.3 61.9/60.1 61.9/51.9 66.3/57.2
V2X-ViT[35] 84.1/80.6 84.5/80.2 38.2/15.6 38.7/15.7 41.4/37.0 54.6/53.4 54.5/44.4 59.3/49.7
CoAlign[21] 83.6/80.8 83.5/82.0 37.4/17.1 41.1/17.4 50.1/36.1 57.0/54.4 57.0/44.7 60.5/51.3
ERMVP[42] 86.7/84.0 84.7/82.0 50.6/23.5 52.2/27.2 41.7/38.7 55.7/55.0 59.7/48.7 64.2/54.7
FocalComm(ours) 90.0/87.0 91.3/87.5 53.9/27.1 58.5/29.5 50.5/42.3 60.8/57.4 64.8/52.1 70.2/58.1
Table2. PerformancecomparisononV2X-RealdatasetforVehicle-to-Vehicle(V2V)andInfrastructure-to-Infrastructure(I2I)communi-
cationscenarios.ResultsshowAP@0.3/AP@0.5format.ForFocalComm,I2Icorrespondstoournormalcollaborativesetup.Bestresults
areinboldface.
evolution of instance detection across stages, using color QAFF alone achieves 65.5% AP@0.3 (+4.2% over base-
codingtodistinguishbetweencars(green),pedestrians(ma- line). The full model combining both HIM and QAFF
genta),andtrucks(blue).WeobservethatStage1capturesa reaches 67.6% AP@0.3, demonstrating synergy between
broadersetofpotentialinstances,whileStages2and3pro- the components with an additional 1.4-2.1% gain over in-
gressivelyrefineandfocusonpreviouslyundetectedcases. dividual components. The improvements are particularly
Thefourthcolumndisplaysthegeneratedqueryfeaturesas notable for pedestrian detection (from 31.8% to 57.4%
heatmapsalongdetectionoutput,wherebrighterregionsin- AP@0.3) and truck detection (from 21.2% to 53.9%), val-
dicatehigherweights. idating our focus on hard instance mining for challenging
objects.
4.4.AblationStudy
Core Component Analysis. To validate the effective- Compression Analysis. To evaluate the communication
ness of our key components, we conduct ablation studies efficiencyofFocalComm,weanalyzethetrade-offbetween
showing the incremental contribution of each module. As detectionperformanceandfeaturecompressionratios. Fig-
shown in Table 3, starting from a no-collaboration base- ure 4 shows how our method’s performance varies across
linewith42.2%overallAP@0.3,basiccollaborativefusion different compression levels from 1× (no compression) to
(F-Cooper) improves performance to 61.3% (+19.1% ab- 64× compression. We observe that FocalComm maintains
solute). Adding HIM alone to collaboration yields 66.2% robustperformanceupto8×compression,withonlya2.5%
AP@0.3(+4.9%overbaselinecollaboration),whileadding dropinAP@0.3(from67.6%to65.9%)andminimaldegra-

Figure3. Visualizationofourmulti-stageHardInstanceMining(HIM)processandqueryfeaturegeneration. Thefigureshowsresults
fromtwoagents(rows)acrossthreeHIMstages(firstthreecolumns),withdetectionscolor-codedasCar(green),Pedestrian(magenta),
andTruck(blue).Thefourthcolumnshowsqueryfeatureheatmapswherebrightercolorsindicatehigherattentionweights.Therightmost
columnprovidesdetectionresults. Thisprogressiondemonstrateshowourmodelsystematicallyrefinesdetectionfocusacrossstagesina
multi-agentsetup.
|     |     |     |     | Method          |     | Car       | Pedestrian | Truck     | Overall   |
| --- | --- | --- | --- | --------------- | --- | --------- | ---------- | --------- | --------- |
|     |     |     |     | NoCollaboration |     | 73.7/68.4 | 31.8/13.9  | 21.2/15.7 | 42.2/32.7 |
ComponentAnalysis
|     |     |     |     | +Collab(baseline) |          | 88.3/85.6           | 47.8/22.7 | 47.9/46.1 | 61.3/51.4        |
| --- | --- | --- | --- | ----------------- | -------- | ------------------- | --------- | --------- | ---------------- |
|     |     |     |     | +Collab+HIM       |          | 91.5/88.8           | 54.6/26.6 | 52.6/48.7 | 66.2/54.7        |
|     |     |     |     | +Collab+QAFF      |          | 91.2/88.2           | 52.7/23.7 | 48.7/45.1 | 65.5/54.0        |
|     |     |     |     | FullModel(+Both)  |          | 91.5/89.6           | 57.4/27.3 | 53.9/51.6 | 67.6/56.1        |
|     |     |     |     | Table 3.          | Ablation | studies on V2X-Real |           | test set  | for the vehicle- |
centricapproach.ResultsshowAP@0.3/AP@0.5foreachclass.
Figure4.Performancevscompressiontrade-offanalysisonV2X- awarefeatureexchange. OurprogressiveHIMmoduleand
Realdataset. FocalCommmaintainsrobustperformanceupto8× QAFF mechanism achieve state-of-the-art results 67.6%
|             |                           |               |           | mAP@0.3 | on V2X-Real | (5.6% | improvement) |     | with strong |
| ----------- | ------------------------- | ------------- | --------- | ------- | ----------- | ----- | ------------ | --- | ----------- |
| compression | with minimal degradation, | demonstrating | effective |         |             |       |              |     |             |
communicationefficiencyforpracticalV2Xdeployment. performance in both V2V (64.8%) and I2I (70.2%) sce-
|     |     |     |     | narios. FocalComm |     | excels | at safety-critical |     | pedestrian de- |
| --- | --- | --- | --- | ----------------- | --- | ------ | ------------------ | --- | -------------- |
tection(57.4%AP@0.3,80%relativeimprovement)while
dationinAP@0.5(from56.1%to54.4%). Evenataggres- maintainingrobustperformanceunder8×compression.
| sive 32× compression, | the method | retains 62.1% | AP@0.3 |     |     |     |     |     |     |
| --------------------- | ---------- | ------------- | ------ | --- | --- | --- | --- | --- | --- |
and48.9%AP@0.5,demonstratingtheeffectivenessofour Limitations. Our evaluation focuses on LiDAR-based
hard instance-focused feature selection. This analysis val- datasets;extendingtocamera-onlyormultimodalfusionre-
idatesthatFocalCommcanoperateefficientlyunderband-
|     |     |     |     | mains future | work, | along with | formal | theoretical | analysis |
| --- | --- | --- | --- | ------------ | ----- | ---------- | ------ | ----------- | -------- |
widthconstraintswhilemaintainingstrongdetectionperfor- ofHIMconvergenceandevaluationunderadverseweather
mance,makingitpracticalforreal-worldV2Xdeployment conditions. Future work will explore hard-instance aware
scenarios. message packing, multimodal extensions, and theoretical
groundingforreal-worldV2Xdeployment.
5.Conclusion
|     |     |     |     | Acknowledgment. |     | This work | was | supported | by US DOT |
| --- | --- | --- | --- | --------------- | --- | --------- | --- | --------- | --------- |
WepresentedFocalComm,anovelmulti-agentcollabo- Safety21UniversityTransportationCenter,CarnegieMel-
rative perception framework that prioritizes hard instance- lonUniversity,Pittsburgh,PA,USA.

References [12] Yue Hu, Shaoheng Fang, Zixing Lei, Yiqi Zhong, and Si-
hengChen.Where2comm:Communication-efficientcollab-
[1] Xuyang Bai, Zeyu Hu, Xinge Zhu, Qingqiu Huang, Yilun orativeperceptionviaspatialconfidencemaps. InAdvances
Chen,HongboFu,andChiew-LanTai.TransFusion:Robust
|              |     |        |     |           |           |      |        | in Neural | Information |     | Processing | Systems. | NeurIPS, | 2022. |
| ------------ | --- | ------ | --- | --------- | --------- | ---- | ------ | --------- | ----------- | --- | ---------- | -------- | -------- | ----- |
| LiDAR-camera |     | fusion | for | 3D object | detection | with | trans- |           |             |     |            |          |          |       |
1,2,6,7
| formers. | In  | Proceedings |     | of the IEEE/CVF |     | Conference | on  |     |     |     |     |     |     |     |
| -------- | --- | ----------- | --- | --------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
ComputerVisionandPatternRecognition.IEEE,2022. 4,5 [13] YueHu,JuntongPeng,SifeiLiu,JunhaoGe,SiLiu,andSi-
|     |     |     |     |     |     |     |     | hengChen. |     | Communication-efficientcollaborativepercep- |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------------------------------------------- | --- | --- | --- | --- |
[2] HolgerCaesar,VarunBankiti,AlexH.Lang,SourabhVora, tionviainformationfillingwithcodebook. InProceedings
VeniceErinLiong,QiangXu,AnushKrishnan,YuPan,Gi- oftheIEEE/CVFConferenceonComputerVisionandPat-
ancarlo Baldan, and Oscar Beijbom. nuScenes: A multi- ternRecognition,pages15481–15490.IEEE,2024.
2
| modal | dataset | for autonomous |     | driving. | In  | Proceedings | of  |     |     |     |     |     |     |     |
| ----- | ------- | -------------- | --- | -------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
theIEEE/CVFConferenceonComputerVisionandPattern [14] TaehoKimandJooheeKim. BEVFusionwithdualhardin-
|     |     |     |     |     |     |     |     | stance | probing | for multimodal |     | 3D object | detection. | IEEE |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------- | -------------- | --- | --------- | ---------- | ---- |
Recognition,pages11618–11628,Seattle,WA,2020.IEEE.
|     |     |     |     |     |     |     |     | Access,13,2025. |     | 3   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- |
1
|     |     |     |     |     |     |     |     | [15] Diederik | P.  | Kingma | and Jimmy | Ba. | Adam: A | method for |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------ | --------- | --- | ------- | ---------- |
[3] ZhaoweiCaiandNunoVasconcelos.CascadeR-CNN:Delv-
|                                    |     |     |     |     |                    |     |     | stochasticoptimization.                        |     |     | InProceedingsoftheInternational |     |     |     |
| ---------------------------------- | --- | --- | --- | --- | ------------------ | --- | --- | ---------------------------------------------- | --- | --- | ------------------------------- | --- | --- | --- |
| ingintohighqualityobjectdetection. |     |     |     |     | InProceedingsofthe |     |     |                                                |     |     |                                 |     |     |     |
|                                    |     |     |     |     |                    |     |     | ConferenceonLearningRepresentations.ICLR,2015. |     |     |                                 |     |     | 5   |
IEEEConferenceonComputerVisionandPatternRecogni-
|                                        |               |                                     |         |            |             |            |     | [16] XianghaoKong,WentaoJiang,JinrangJia,YifengShi,Run- |            |                                        |                           |            |              |               |
| -------------------------------------- | ------------- | ----------------------------------- | ------- | ---------- | ----------- | ---------- | --- | ------------------------------------------------------- | ---------- | -------------------------------------- | ------------------------- | ---------- | ------------ | ------------- |
| tion,pages6154–6162.IEEE,2018.         |               |                                     |         |            | 2           |            |     |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | sheng                                                   | Xu,        | and Si                                 | Liu. DUSA:                | Decoupled  | unsupervised |               |
| [4] QiChen,                            | XuMa,         | SihaiTang,                          |         | JingdaGuo, |             | QingYang,  | and |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | sim2real                                                | adaptation |                                        | for vehicle-to-everything |            |              | collaborative |
| Song                                   | Fu. F-Cooper: |                                     | Feature | based      | cooperative | perception |     |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | perception.                                             |            | InProceedingsoftheACMInternationalCon- |                           |            |              |               |
| for autonomous                         |               | vehicle                             | edge    | computing  | system      | using      | 3D  |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | ferenceonMultimedia,pages1943–1954.ACM,2023.            |            |                                        |                           |            |              | 2             |
| pointclouds.                           |               | InProceedingsoftheIEEE/ACMSymposium |         |            |             |            |     |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | [17] Zixing                                             | Lei,       | Shunli                                 | Ren, Yue                  | Hu, Wenjun | Zhang,       | and Si-       |
| onEdgeComputing,pages88–100.IEEE,2019. |               |                                     |         |            |             | 6,7        |     |                                                         |            |                                        |                           |            |              |               |
|                                        |               |                                     |         |            |             |            |     | hengChen.                                               |            | Latency-awarecollaborativeperception.  |                           |            |              | InPro-        |
[5] RunjianChen,YaoMu,RunsenXu,WenqiShao,Chenhan ceedings of the European Conference on Computer Vision.
| Jiang,HangXu,ZhenguoLi,andPingLuo. |     |     |     |     |     | CO3:Coopera- |     |                |     |     |     |     |     |     |
| ---------------------------------- | --- | --- | --- | --- | --- | ------------ | --- | -------------- | --- | --- | --- | --- | --- | --- |
|                                    |     |     |     |     |     |              |     | Springer,2022. |     | 1,2 |     |     |     |     |
tiveunsupervised3Drepresentationlearningforautonomous
driving. InProceedingsoftheInternationalConferenceon [18] YimingLi,ShunliRen,PengxiangWu,SihengChen,Chen
|                                    |     |     |     |     |     |     |     | Feng,                          | and Wenjun | Zhang. | Learning |                       | distilled collaboration |     |
| ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------ | ---------- | ------ | -------- | --------------------- | ----------------------- | --- |
| LearningRepresentations.ICLR,2023. |     |     |     |     | 2   |     |     |                                |            |        |          |                       |                         |     |
|                                    |     |     |     |     |     |     |     | graphformulti-agentperception. |            |        |          | InAdvancesinNeuralIn- |                         |     |
[6] Yilun Chen, Zhiding Yu, Yukang Chen, Shiyi Lan, An- formationProcessingSystems.NeurIPS,2021. 2
| ima       | Anandkumar, |          | Jiaya Jia, | and      | Jose M Alvarez. |        | Focal- |                                                        |     |                                   |     |     |     |        |
| --------- | ----------- | -------- | ---------- | -------- | --------------- | ------ | ------ | ------------------------------------------------------ | --- | --------------------------------- | --- | --- | --- | ------ |
|           |             |          |            |          |                 |        |        | [19] Tsung-YiLin,PriyaGoyal,RossGirshick,KaimingHe,and |     |                                   |     |     |     |        |
| Former3D: |             | Focusing | on hard    | instance | for 3D          | object | detec- |                                                        |     |                                   |     |     |     |        |
|           |             |          |            |          |                 |        |        | PiotrDolla´r.                                          |     | Focallossfordenseobjectdetection. |     |     |     | InPro- |
tion. InProceedingsoftheIEEEInternationalConference
ceedingsoftheIEEEInternationalConferenceonComputer
| onComputerVision.IEEE,2023. |             |            |            |           | 2,3            |             |         |                                               |               |         |                            |        |             |         |
| --------------------------- | ----------- | ---------- | ---------- | --------- | -------------- | ----------- | ------- | --------------------------------------------- | ------------- | ------- | -------------------------- | ------ | ----------- | ------- |
|                             |             |            |            |           |                |             |         | Vision,pages2980–2988,Venice,Italy,2017.IEEE. |               |         |                            |        |             | 2       |
| [7] Jiaxun                  | Cui,        | Hang Qiu,  | Dian       | Chen,     | Peter Stone,   | and         | Yuke    |                                               |               |         |                            |        |             |         |
|                             |             |            |            |           |                |             |         | [20] Yifan                                    | Lu,           | Yue Hu, | Yiqi Zhong,                | Dequan | Wang,       | Yanfeng |
| Zhu.                        | Coopernaut: |            | End-to-end |           | driving with   | cooperative |         |                                               |               |         |                            |        |             |         |
|                             |             |            |            |           |                |             |         | Wang,andSihengChen.                           |               |         | HEAL:Anextensibleframework |        |             |         |
| perception                  | for         | networked  |            | vehicles. | In Proceedings |             | of the  |                                               |               |         |                            |        |             |         |
|                             |             |            |            |           |                |             |         | for open                                      | heterogeneous |         | collaborative              |        | perception. | In Pro- |
| IEEE/CVF                    |             | Conference | on         | Computer  | Vision         | and         | Pattern |                                               |               |         |                            |        |             |         |
ceedingsoftheInternationalConferenceonLearningRep-
Recognition,pages17252–17262.IEEE,2022. 2 resentations.ICLR,2024.
2
[8] LueFan,ZiqiPang,TianyuanZhang,Yu-XiongWang,Hang
|       |      |       |        |       |               |     |        | [21] YifanLu, | QuanhaoLi,  |     | BaoanLiu,       | MehrdadDianati, |                  | Chen |
| ----- | ---- | ----- | ------ | ----- | ------------- | --- | ------ | ------------- | ----------- | --- | --------------- | --------------- | ---------------- | ---- |
| Zhao, | Feng | Wang, | Naiyan | Wang, | and Zhaoxiang |     | Zhang. |               |             |     |                 |                 |                  |      |
|       |      |       |        |       |               |     |        | Feng,         | SihengChen, |     | andYanfengWang. |                 | Robustcollabora- |      |
Embracingsinglestride3Dobjectdetectorwithsparsetrans-
|         |     |             |     |              |     |            |     | tive3Dobjectdetectioninpresenceofposeerrors. |     |     |     |     |     | InPro- |
| ------- | --- | ----------- | --- | ------------ | --- | ---------- | --- | -------------------------------------------- | --- | --- | --- | --- | --- | ------ |
| former. | In  | Proceedings | of  | the IEEE/CVF |     | Conference | on  |                                              |     |     |     |     |     |        |
ceedingsoftheIEEEInternationalConferenceonRobotics
Computer Vision and Pattern Recognition, pages 8458– andAutomation.IEEE,2023. 2,6,7
| 8468.IEEE,2022. |     | 2   |     |     |     |     |     |                                                  |     |     |     |     |     |          |
| --------------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- | -------- |
|                 |     |     |     |     |     |     |     | [22] NationalHighwayTrafficSafetyAdministration. |     |     |     |     |     | Overview |
[9] LueFan,FengWang,NaiyanWang,andZhaoxiangZhang. of motor vehicle traffic crashes in 2022. https://
| Fullysparse3Dobjectdetection. |     |     |     |     | InAdvancesinNeuralIn- |     |     |     |     |     |     |     |     |     |
| ----------------------------- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
crashstats.nhtsa.dot.gov,2024.Accessed:2024-
| formationProcessingSystems.NeurIPS,2022. |     |     |     |     |     | 2   |     |        |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
|                                          |     |     |     |     |     |     |     | 10-01. | 2   |     |     |     |     |     |
[10] AndreasGeiger, PhilipLenz, andRaquelUrtasun. Arewe [23] Jiangmiao Pang, Kai Chen, Jianping Shi, Huajun Feng,
readyforautonomousdriving?theKITTIvisionbenchmark Wanli Ouyang, and Dahua Lin. Libra R-CNN: Towards
suite. pages3354–3361,2012. 1 balanced learning for object detection. In Proceedings of
theIEEE/CVFConferenceonComputerVisionandPattern
[11] YushanHan,HuiZhang,HuifangLi,YiJin,CongyanLang,
andYidongLi.Collaborativeperceptioninautonomousdriv- Recognition,pages821–830.IEEE,2019. 2
ing: Methods, datasets, and challenges. IEEE Intelligent [24] Dereje Shenkut and B. V. K. Vijaya Kumar. ReVQom:
TransportationSystemsMagazine,15(6):131–151,2023. 1 Residual vector quantization for communication-efficient

multi-agent perception. arXiv preprint arXiv:2509.21464, [34] Runsheng Xu, Jinlong Li, Xiaoyu Dong, Hongkai Yu, and
| 2025.       | 2       |     |               |     |        |               | JiaqiMa. | Bridgingthedomaingapformulti-agentpercep-     |     |     |     |     |     |
| ----------- | ------- | --- | ------------- | --- | ------ | ------------- | -------- | --------------------------------------------- | --- | --- | --- | --- | --- |
|             |         |     |               |     |        |               | tion.    | InProceedingsoftheIEEEInternationalConference |     |     |     |     |     |
| [25] Dereje | Shenkut | and | B.V.K. Vijaya |     | Kumar. | Impact of la- |          |                                               |     |     |     |     |     |
tency and bandwidth limitations on the safety performance onRoboticsandAutomation.IEEE,2023. 1,2,6,7
ofcollaborativeperception. InProceedingsoftheInterna- [35] RunshengXu,HaoXiang,ZhengzhongTu,XinXia,Ming-
tional Conference on Computer Communications and Net- HsuanYang,andJiaqiMa. V2X-ViT:Vehicle-to-everything
works,pages1–8.IEEE,2024. 2 cooperative perception with vision transformer. In Pro-
|              |              |     |         |        |     |                | ceedings       | of the | European | Conference | on  | Computer | Vision. |
| ------------ | ------------ | --- | ------- | ------ | --- | -------------- | -------------- | ------ | -------- | ---------- | --- | -------- | ------- |
| [26] Abhinav | Shrivastava, |     | Abhinav | Gupta, | and | Ross Girshick. |                |        |          |            |     |          |         |
|              |              |     |         |        |     |                | Springer,2022. |        | 1,2,6,7  |            |     |          |         |
Trainingregion-basedobjectdetectorswithonlinehardex-
ample mining. In Proceedings of the IEEE Conference on [36] RunshengXu,HaoXiang,XinXia,XuHan,JinlongLi,and
|          |        |     |         |              |     |                | JiaqiMa. | OPV2V:Anopenbenchmarkdatasetandfusion |     |     |     |     |     |
| -------- | ------ | --- | ------- | ------------ | --- | -------------- | -------- | ------------------------------------- | --- | --- | --- | --- | --- |
| Computer | Vision | and | Pattern | Recognition, |     | pages 761–769, |          |                                       |     |     |     |     |     |
LasVegas,NV,2016.IEEE. 2 pipelineforperceptionwithvehicle-to-vehiclecommunica-
|                                            |     |     |     |     |     |             | tion.                              | InProceedingsoftheIEEEInternationalConference |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | ----------- | ---------------------------------- | --------------------------------------------- | --- | --- | --- | --- | --- |
| [27] ZhiyingSong,LeiYang,FuxiWen,andJunLi. |     |     |     |     |     | TraF-Align: |                                    |                                               |     |     |     |     |     |
|                                            |     |     |     |     |     |             | onRoboticsandAutomation.IEEE,2022. |                                               |     |     |     | 2   |     |
Trajectory-awarefeaturealignmentforasynchronousmulti-
agent perception. In Proceedings of the IEEE/CVF Con- [37] YanYan,YuxingMao,andBoLi. SECOND:Sparselyem-
ferenceonComputerVisionandPatternRecognition.IEEE, beddedconvolutionaldetection. Sensors,18(10),2018. 5
2025. 2 [38] Dingkang Yang, Kun Yang, Yuzheng Wang, Jing Liu, Zhi
Xu,RongbinYin,PengZhai,andLihuaZhang.How2comm:
| [28] Pei | Sun, Henrik | Kretzschmar, |     | Xerxes | Dotiwalla, | Aurelien |     |     |     |     |     |     |     |
| -------- | ----------- | ------------ | --- | ------ | ---------- | -------- | --- | --- | --- | --- | --- | --- | --- |
Chouard,VijaysaiPatnaik,PaulTsui,JamesGuo,YinZhou, Communication-efficientandcollaboration-pragmaticmulti-
YuningChai,BenjaminCaine,etal.Scalabilityinperception agent perception. In Advances in Neural Information Pro-
forautonomousdriving: Waymoopendataset. InProceed- cessingSystems.NeurIPS,2023. 2
ingsoftheIEEE/CVFConferenceonComputerVisionand
[39] LeiYang,XinyuZhang,JunLi,ChenWang,JiaqiMa,Zhiy-
| Pattern | Recognition, |     |     |     |     |     |     |     |     |     |     |     |     |
| ------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
pages 2446–2454, Seattle, WA, 2020. ingSong,TongZhao,ZiyingSong,LiWang,MoZhou,Yang
| IEEE. | 1   |     |     |     |     |     | Shen,andChenLv.V2X-Radar:Amulti-modaldatasetwith |     |     |     |     |     |     |
| ----- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- |
[29] Tianhang Wang, Guang Chen, Kai Chen, Zhengfa Liu, 4Dradarforcooperativeperception. InAdvancesinNeural
Bo Zhang, Alois Knoll, and Changjun Jiang. UMC: A InformationProcessingSystems.NeurIPS,2025. 2
| unified | bandwidth-efficient |     | and | multi-resolution |     | based col- |     |     |     |     |     |     |     |
| ------- | ------------------- | --- | --- | ---------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
[40] HaibaoYu,YizhenLuo,MaoShu,YiyiHuo,ZebangYang,
| laborative | perception |     | framework. |     | In Proceedings | of the |     |     |     |     |     |     |     |
| ---------- | ---------- | --- | ---------- | --- | -------------- | ------ | --- | --- | --- | --- | --- | --- | --- |
YifengShi,ZhenglongGuo,HanyuLi,XingHu,JiruiYuan,
| IEEE/CVF |     | International | Conference |     | on Computer | Vision, |             |      |           |     |               |         |     |
| -------- | --- | ------------- | ---------- | --- | ----------- | ------- | ----------- | ---- | --------- | --- | ------------- | ------- | --- |
|          |     |               |            |     |             |         | and Zaiqing | Nie. | DAIR-V2X: |     | A large-scale | dataset | for |
pages8187–8196.IEEE,2023. 2 vehicle-infrastructure cooperative 3D object detection. In
ProceedingsoftheIEEE/CVFConferenceonComputerVi-
| [30] Tsun-Hsuan |     | Wang, | Sivabalan | Manivasagam, |     | Ming Liang, |     |     |     |     |     |     |     |
| --------------- | --- | ----- | --------- | ------------ | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
Bin Yang, Wenyuan Zeng, and Raquel Urtasun. V2VNet: sion and Pattern Recognition, pages 21361–21370. IEEE,
| Vehicle-to-vehicle            |     | communication                          |     | for     | joint | perception and | 2022.          | 5            |                                  |             |          |     |        |
| ----------------------------- | --- | -------------------------------------- | --- | ------- | ----- | -------------- | -------------- | ------------ | -------------------------------- | ----------- | -------- | --- | ------ |
| prediction.                   |     | InProceedingsoftheEuropeanConferenceon |     |         |       |                |                |              |                                  |             |          |     |        |
|                               |     |                                        |     |         |       |                | [41] Yunshuang | Yuan,        | Yan                              | Xia, Daniel | Cremers, | and | Monika |
| ComputerVision.Springer,2020. |     |                                        |     | 2,5,6,7 |       |                |                |              |                                  |             |          |     |        |
|                               |     |                                        |     |         |       |                | Sester.        | SparseAlign: | Afullysparseframeworkforcoopera- |             |          |     |        |
[31] Qiming Xia, Wei Ye, Hai Wu, Shijia Zhao, Leyuan Xing, tiveobjectdetection. InProceedingsoftheIEEE/CVFCon-
ferenceonComputerVisionandPatternRecognition.IEEE,
XunHuang,JinhaoDeng,XinLi,ChengluWen,andCheng
| Wang. | HINTED: | Hard | instance | enhanced |     | detector with | 2025. | 2   |     |     |     |     |     |
| ----- | ------- | ---- | -------- | -------- | --- | ------------- | ----- | --- | --- | --- | --- | --- | --- |
mixed-densityfeaturefusionforsparsely-supervised3Dob-
|                |     |                                      |     |     |     |     | [42] Jingyu       | Zhang, | Kun Yang,                        | Yilei | Wang, Hanqi | Wang, | Peng |
| -------------- | --- | ------------------------------------ | --- | --- | --- | --- | ----------------- | ------ | -------------------------------- | ----- | ----------- | ----- | ---- |
| jectdetection. |     | InProceedingsoftheIEEE/CVFConference |     |     |     |     |                   |        |                                  |       |             |       |      |
|                |     |                                      |     |     |     |     | Sun,andLiangSong. |        | Ermvp:Communication-efficientand |       |             |       |      |
onComputerVisionandPatternRecognition,pages15321–
collaboration-robustmulti-vehicleperceptioninchallenging
15330.IEEE,2024. 2,3 environments. InProceedingsoftheIEEE/CVFConference
onComputerVisionandPatternRecognition(CVPR),pages
[32] HaoXiang,ZhaoliangZheng,XinXia,RunshengXu,Letian
Gao, Zewei Zhou, Xu Han, Xinkai Ji, Mingxi Li, Zonglin 12575–12584,June2024. 6,7
| Meng,   | Li Jin,       | Mingyue   | Lei,          | Zhaoyang | Ma,     | Zihang He,      |                                         |     |              |           |     |            |        |
| ------- | ------------- | --------- | ------------- | -------- | ------- | --------------- | --------------------------------------- | --- | ------------ | --------- | --- | ---------- | ------ |
|         |               |           |               |          |         |                 | [43] Yin Zhou                           | and | Oncel Tuzel. | VoxelNet: |     | End-to-end | learn- |
| Haoxuan | Ma,           | Yunshuang | Yuan,         | Yingqian |         | Zhao, and Ji-   |                                         |     |              |           |     |            |        |
|         |               |           |               |          |         |                 | ingforpointcloudbased3Dobjectdetection. |     |              |           |     | InProceed- |        |
| aqi     | Ma. V2X-Real: |           | A large-scale |          | dataset | for vehicle-to- |                                         |     |              |           |     |            |        |
ingsoftheIEEEConferenceonComputerVisionandPattern
everything cooperative perception. In Proceedings of the Recognition,pages4490–4499.IEEE,2018. 5
EuropeanConferenceonComputerVision,pages455–470.
| Springer,2024. |       | 2,5,6    |         |             |          |             |     |     |     |     |     |     |     |
| -------------- | ----- | -------- | ------- | ----------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
| [33] Li Xiang, | Junbo | Yin,     | Wei Li, | Cheng-Zhong |          | Xu, Ruigang |     |     |     |     |     |     |     |
| Yang,          | and   | Jianbing | Shen.   | DI-V2X:     | Learning | domain-     |     |     |     |     |     |     |     |
invariantrepresentationforvehicle-infrastructurecollabora-
| tive3Dobjectdetection. |     |     | arXivpreprintarXiv:2312.15742, |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023.                  | 1,2 |     |                                |     |     |     |     |     |     |     |     |     |     |