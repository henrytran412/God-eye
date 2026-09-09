3054 IEEEROBOTICSANDAUTOMATIONLETTERS,VOL.7,NO.2,APRIL2022
Keypoints-Based Deep Feature Fusion
for Cooperative Vehicle Detection of
Autonomous Driving
YunshuangYuan ,HaoCheng,andMonikaSester
Abstract—Sharing collective perception messages (CPM) be- using the data collected by these sensors mounted on a single
tween vehicles is investigated to decrease occlusions so as to im- ego vehicle has many limitations, such as occlusion, limited
provetheperceptionaccuracyandsafetyofautonomousdriving.
sensorobservationrange,andnoise.Inthisregard,cooperative
However, highly accurate data sharing and low communication
perceptionbasedonconnectedandautomatedvehicles(CAVs)
overhead is a big challenge for collective perception, especially
whenreal-timecommunicationisrequiredamongconnectedand caneffectivelymitigatetheseproblemsbysharingsensedinfor-
automated vehicles. In this letter, we propose an efficient and mation collected from different viewing directions of multiple
effective keypoints-based deep feature fusion framework built AVsinanetwork.Theperceivedinformationissharedamong
on the 3D object detector PV-RCNN, called Fusion PV-RCNN
vehicles via Collective Perception Messages (CPMs). In this
(FPV-RCNNforshort),forcollectiveperception.Weintroducea
way,theaccuracyandreliabilityrequirementsofthesensorson
high-performanceboundingboxproposalmatchingmoduleanda
keypoints selection strategy to compress the CPM size and solve eachvehiclecanberelaxed,andthereforethepriceofeachAVis
the multi-vehicle data fusion problem. Besides, we also propose loweredaswell[2].However,thechallengingpartofcooperative
an effective localization error correction module based on the perception is defining the information to be shared and fusing
maximum consensus principle to increase the robustness of the
the shared information via a limited communication network
datafusion.Comparedtoabird’s-eyeview(BEV)keypointsfea-
bandwidth. Hence, the goal is to obtain the best perception
turefusion,FPV-RCNNachievesimproveddetectionaccuracyby
about9%atahighevaluationcriterion(IoU0.7)onthesynthetic performancewiththeleastdatatransmissioninthenetworkof
dataset COMAP dedicated to collective perception. In addition, cooperativeagents.
its performance is comparable to two raw data fusion baselines Accurate data sharing and low communication overhead is
that have no data loss in sharing. Moreover, our method also
still a bottleneck for cooperative vehicle detection demanding
significantly decreases the CPM size to less than 0.3 KB, and is
real-timecommunicationinautonomousdriving.Intheory,shar-
thus about 50 times smaller than the BEV feature map sharing
usedinpreviousworks.EvenwithfurtherdecreasedCPMfeature ingrawdatagivesthebestperformancebecausenoinformation
channels, i. e., from 128 to 32, the detection performance does islost.Butthiscaneasilycongestthecommunicationnetwork
notshowapparentdrops.Thecodeofourmethodisavailableat with heavy data loads. In contrast, sharing the fully processed
https://github.com/YuanYunshuang/FPV_RCNN.
data, e.g., detected objects, needs fewer communication re-
IndexTerms—Sensorfusion,sensornetworks,objectdetection, sources.Nevertheless,object-wisefusionisverysensitivetothe
segmentationandcategorization. localizationnoiseoftheagents.Matchingthedetectedobjects
coming from different agents can be very difficult, especially
thosethatareinaccuratelydetectedbydistantsensors.Asatrade-
I. INTRODUCTION
off, deep features extracted by deep neural networks from the
UNDERSTANDING the surrounding environment is one rawdatacandecreasetheamountofdatatobesharedandatthe
of the most important tasks of autonomous driving, es- sametimemaintainarelativelyhighperformanceofdatafusion.
peciallyforthoseautomatedvehicles(AV)drivingincomplex Previous works [3]–[5] achieve this by contracting bird’s-eye
real-world situations. Such an AV is normally equipped with view(BEV)deepfeaturesmapswhichare,however,verysparse
differentsensorslikecameras,LiDARs,andSonarsinorderto andcanbefurthercompressedtoavoidredundancy.Moreover,
sensetheworld[1].However,perceivingtheenvironmentonly due to the low resolution, fusing such feature maps may even
failtopredictaccurateboundingboxes.Tothisend,thisletter
proposesamorerobustdeepfeaturesharingandfusionframe-
ManuscriptreceivedSeptember9,2021;acceptedDecember29,2021.Date
workbyextendingtheestablishedframeworkPV-RCNN[6]to
ofpublicationJanuary14,2022;dateofcurrentversionFebruary4,2022.This
letterwasrecommendedforpublicationbyAssociateEditorG.Costanteand colletiveperceptionscenarios.OurframeworkusesPointNet[7]
EditorE.Marchanduponevaluationofthereviewers’comments.Thiswork andpointsetabstraction[8]toaggregatetheinformationfrom
wassupportedbytheProjectsDFGRTC1931SocialCarsandDFGGRK2159
multi-scale receptive fields for the selected high accurate 3D
i.c.sens.(Correspondingauthor:HaoCheng.)
The authors are with the Institute of Cartography and Geoinfor- keypointsfromdifferentpointclouds,whicharethensharedand
matics, Leibniz University Hannover, 30167 Hannover, Germany (e- fusedtogeneratemoreaccuratedetection.Incomparisontothe
mail:yunshuang.yuan@ikg.uni-hannover.de;hao.cheng@ikg.uni-hannover.de;
BEVkeypointsfusion,withreducedcommunicationoverhead
monika.sester@ikg.uni-hannover.de).
DigitalObjectIdentifier10.1109/LRA.2022.3143299 our3Dkeypointsfusionstillachieveshigherdetectionaccuracy.
2377-3766©2022IEEE.Personaluseispermitted,butrepublication/redistributionrequiresIEEEpermission.
Seehttps://www.ieee.org/publications/rights/index.htmlformoreinformation.
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore. Restrictions apply.

YUANetal.:KEYPOINTS-BASEDDEEPFEATUREFUSIONFORCOOPERATIVEVEHICLEDETECTIONOFAUTONOMOUSDRIVING 3055
acrossthevehiclesatanyplace[11].OurworkfocusesonV2V
communicationforobjectdetection.
InV2Vcommunication,differentapproachesareproposedto
communicatethedatainaCAVnetwork.Inthisletter,wesort
datafusionstrategiesas(1)rawdatasharing,(2)fullyprocessed
data,suchasdetectedobjects,and(3)half-processeddata.The
studybyMarvastietal. [4]showsthatrawdatasharingprovides
rich information for object detection. It, however, consumes
large bandwidth and is not feasible for autonomous driving
that requires real-time communication. Contrary to raw data
sharing,[12]–[14]proposetoonlysharethedetectedobjectsfor
moreefficientcommunication.However,theworkbyWangetal.
[5]has shown thatthis latefusionoffullyprocessed data per-
formsworsethaneitherearlyrawdatafusionorhalf-processed
datafusion.
In order to reduce communication resource consumption
Fig. 1. The detection result of an exemplary frame with two CAVs. The
without a compromise of performance, sharing half-processed
vehicleintheyellowdashedcirclesharesCPMtotheegovehicle(upperright).
According to the IoUs (marked in the boxes) against the ground truth, our data is further explored. In an extreme case, the objects mis-
proposedmethodofthe3DkeypointsfusionoutperformstheBEVkeypoints detectedbyallindependentsensorscanbedetectedafterthisdata
fusionbyalargemarginforimprovingtheegovehicle’sdetection.
fusion[3].Forexample,insteadoffusingthedetectedobjects,
Chenetal. [3]extendtheirpreviouswork[14]byfusingvoxel
featuresanddeepfeatureslearnedusingaDeepNeuralNetwork
Anexampletestedonthesyntheticcollectiveperceptiondataset (DNN)forcooperativeperception.Ontheonehand,significant
COMAP[9]isshowninFig.1. performance improvement has been shown on the real-world
Ourmaincontributionsaresummarizedasfollows: datasets KITTI [15] and T&J [14] only for dedicated traffic
1) We propose a 3D keypoints feature fusion scheme for scenarios, e.g., in a parking lot [14]. On the other hand, these
cooperative vehicle detection to remedy the problem of datasets are not dedicated to collective perception but rather
low bounding box localization accuracy of the schemes to a single egocentric perspective. This is because collective
thatarebasedontheBEVfeaturefusion. perception requires multiple vehicles to share a certain degree
2) Weintroduceakeypointsselectionmoduletoreducethe of field-of-view (FOV) at the same time. But acquiring such a
redundancyofshareddeepfeaturessoastodecreasethe real-worlddatasetnotonlyneedsexpensiveequipmentbutalso
communicationoverhead. needsnumeroushoursofmanuallabelingtoobtaingroundtruth
3) Weproposeanefficientandrobustlocalizationcorrection information. Therefore, many recent works [4], [16] resort to
module and a bounding box matching module that can syntheticdataforamorecomprehensiveempiricalstudy.Data
generate bounding box proposals of high quality for the generatorandsimulationtoolse.g., CARLAandSUMO[17],
deepfeaturefusioninthelaterstage. cannotonlybemanipulatedtogeneratealargeamountofreal-
4) Ourproposed method notonlyoutperforms thestate-of- isticdatainvarioustrafficsituationsforcooperativeperception,
the-artmethodthatusesBEVfeaturefusionforcollective but also provide accurate ground truth information. In [4], the
perceptionwithalargemarginbutalsoreducestheCPM comparison of different data fusion strategies on a simulated
datasizebyalargescale. point cloud dataset generated by CARLA indicates that both
therawdataanddeepfeaturefusionoutperformtheobject-wise
fusion by a big margin, especially when vehicle localization
II. RELATEDWORK
errorsareintroduced.Inaddition,[5]alsoconfirmsthatonthe
Ingeneral,cooperativeperceptioncanbeachievedbymeans simulated dataset LiDARsim [16], sharing compressed deep
ofVehicle-to-Infrastructure(V2I)andVehicle-to-Vehicle(V2V) feature maps achieves high accurate object detection while
communication. V2I communication offers the opportunity to satisfyingcommunicationbandwidthrequirements.
exchange sensory information between an ego vehicle and the Despite the preliminary success of deep feature fusion, the
infrastructure. This helps the ego vehicle go beyond the limi- shared feature maps still contain too much redundancy due to
tations of its own perception system. A successful application theirsparsity.Thesedeepfeaturesarehighlyabstract,whichare
by Yang et al. [10] is the so-called smart intersection, where difficulttobeselected,compressed,andfinallyfusedbyaneural
information for object detection and tracking is shared via the network.Forexample,[3]–[5]triedtoshareintermediatefeature
BEVobservationfromthestaticcamerasattheintersectionto mapsforvehicledetection.Itwasfoundthatthisstrategyisnot
the ego vehicle. These cameras are easy to deploy, whereas robust in providing highly accurate bounding box predictions
their perceptions are limited to traffic scenarios at the specific because the shared feature maps are of low resolution, i. e.,
intersection.Incontrast,V2Vcommunicationisnotlimitedto 8× down-sampled from the raw data. Besides, all previous
thedefinedlocation.InaCAVnetwork,eachvehiclecanbeseen deepfeaturefusionframeworksmentionedaboveevaluatetheir
asanodewithmultiplesensors,thesenseddatacanbeshared performancewithobject-wisefusionwithoutlocalizationerror
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore. Restrictions apply.

| 3056 |     |     |     |     |     |     | IEEEROBOTICSANDAUTOMATIONLETTERS,VOL.7,NO.2,APRIL2022 |     |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- |
Fig.2. Anoverviewofthekeypointsdeepfeaturefusionframework(FPV-RCNN).
| correction         | and have not | provided | the      | implementation |           | details |     |     |     |     |     |
| ------------------ | ------------ | -------- | -------- | -------------- | --------- | ------- | --- | --- | --- | --- | --- |
| of the object-wise | fusion       | method.  | However, |                | different | imple-  |     |     |     |     |     |
mentationsoflocalobjectdetectionandobject-wisefusioncan
greatlyinfluencethefinalresult.Moreover,thelocalizationerror
| can be recovered | without  | much     | effort   | only           | by the | geometry  |     |     |     |     |     |
| ---------------- | -------- | -------- | -------- | -------------- | ------ | --------- | --- | --- | --- | --- | --- |
| of the detected  | vehicles | in       | most of  | the situations |        | as far as |     |     |     |     |     |
| two matchings    | of the   | detected | vehicles | between        | the    | ego and   |     |     |     |     |     |
cooperativevehiclesareavailable.Hence,itisalsoimportantto
analyzethefinalfusionresultwithlocalizationerrorcorrection,
whichisproposedinthisletter.
| To summarize,  | instead     | of       | sharing  | deep features, |                 | we inves- |     |     |     |     |     |
| -------------- | ----------- | -------- | -------- | -------------- | --------------- | --------- | --- | --- | --- | --- | --- |
| tigate sharing | only the    | selected | keypoint | features,      |                 | aiming    | to  |     |     |     |     |
| further reduce | the feature | size     | while    | keeping        | the performance |           |     |     |     |     |     |
for object detection. Moreover, we also introduce localization Fig.3. Featureextractionandselection.
errorsanderrorcorrectiontoguaranteeafaircomparisonofthe
performanceofallfusionmethods.
|     |     |     |     |     |     |     | B. 3DKeypointsDeepFeaturesFusion |           |          |                |           |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --------- | -------- | -------------- | --------- |
|     |     |     |     |     |     |     | The fusion                       | framework | proposed | is built based | on the 3D |
III. METHOD object detector PV-RCNN [6], hence we term it as Fusion
|     |     |     |     |     |     |     | PV-RCNN, | or FPV-RCNN | for short | in the rest of | this letter. |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --------- | -------------- | ------------ |
A. ProblemFormulation
Figure2demonstratesafusionexampleoftwoCAVs.Itisalso
We formulate the collective perception problem in an ego- straightforwardtoextendthisframeworktoanarbitrarynumber
R
centric way. Within a communication range c of the ego- ofCAVs.Asdepictedinthefigure,dataflowsofthetwoCAVs
vehicleC 0,N numberofcooperativeCAVs{C ,C ,...C } arecoloredblueandyellow,respectively.Wefirstextractdeep
|     | v   |     |     |     | 1   | 2 N v |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
as well as the ego CAV have generated the point cloud featuresseparatelyfrompointclouds(Fig.2a)andthenselect
| PC={PC | ,PC | ,...,PC | }   |     | t.  |     |     |     |     |     |     |
| ------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
set 0 1 N at time The bound- and encode the most important features for sharing (Fig. 2 b).
v
ing boxes (BBoxes) of the N vehicles detected based on At last, the shared features are fused for the final detection
i
| PC    |                  |     |         | B    | ={(b | ,s j)|j |             |     |     |     |     |
| ----- | ---------------- | --- | ------- | ---- | ---- | ------- | ----------- | --- | --- | --- | --- |
| i are | called proposals | and | notated | as i |      | j       | = (Fig.2c). |     |     |     |     |
1,...,N i)}. Each instance in B i is a pair which contains one a) Feature extraction: To extract the 3D features of point
detected vehicle b =(x,y,z,w,l,h,r) and its corresponding clouds,weadoptavoxel-basedsparseCNNbackbonenetwork
j
| detectionconfidences |     | j.Inthisnotation,xyzindicatestheBBox |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
from[6]becauseofitshighefficiencyandaccuracy.Thisnet-
center,wlhthedimensions,andr ∈[−π,π]theorientation.In workisdemonstratedinthebottomleftofFig.3.Therawpoint
| ourproposedframework,thecooperativeCAVC |     |     |     |     | i(1≤i≤N |     |     |     |     |     |     |
| --------------------------------------- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- |
v ) cloudisfirstvoxelizedandthenpassedtoablockof3Dsparse
generatesandsharestotheegoCAVC 0theCPM ithatcontains convolutions[18],[19].Theoriginalvoxelfeaturesareencoded
B i,theselectedandaggregateddeepfeatureinformationF iand and8×down-sampledto3Ddeepfeatures.Thefeaturesfromthe
thecoordinatesofK
ikeypointsforlocalizationerrorcorrection. lastsparseconvolutionlayerarethencompressedandprojected
Then ego vehicle C fuses the information of the received toBEVfeatures.
0
CPMswiththelocalinformationandgeneratesthefinalrefined b)Featureselectionandencoding:Theego-detectionmodule
predictionsoftheBBoxes. adopts the detection head from CIA-SSD [20] since it has a
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore.  Restrictions apply.

YUANetal.:KEYPOINTS-BASEDDEEPFEATUREFUSIONFORCOOPERATIVEVEHICLEDETECTIONOFAUTONOMOUSDRIVING 3057
simple structure and can generate better proposals than the
Algorithm1:CooperativeBBoxMatching.
proposal generation module in PV-RCNN. Besides, CIA-SSD
calibrates the detection scores with IoUs which is critical for
Ensure:ℬ=B
1
∪B
2
∪...∪B
N v
,clustersetC =∅,
our matching in Algorithm 1 that uses the scores for merging.
clusterindexk =1,iouthr =0.3,mergedproposalset
This module generates proposals B i which are then utilized
M =∅.
1: whileB(cid:7)=∅do
for selecting feature points. Only the feature points inside the
2: SelectoneBBoxbfromsetB
proposalsareselected,furtherencoded,andcompressedtothe
CPMformattodecreasetheCPMsize. 3: Ck ={(b,(cid:8)s(cid:8))|(b,(cid:8)s(cid:8))∈ (cid:2) B,IoU(b,(cid:8)b)>iouthr }
The details of the feature selection are shown in Fig. 3.
4: B←B\Ck,C ←C {Ck },k =k+1
5: endwhile
FurthestPointsSampling(FPS)isusedtosampleapre-defined
t n o um (cid:4) 2 b ) e . r B N a k s p e ts d o o f n e t v h e e nl s y el d ec is t t e r d ib k u e te y d po s i p n a t r s se in k (cid:4) e 2 yp , o th in e ts V ( o s x te e p l S (cid:4) 1 et 7 6 : : fo I re ← ac { h i C | k (s ⊂ i ,b C i d ) o ∈Ck }
Abstraction(VSA)modulewiththesameparametersisadopted 8: r max =a(cid:3)rgmax r S, S ={s i |i∈I}
from [6] to aggregate deep features for each selected key- 9: S dir1 = I 1 s i1 , I 1 ={i1||r i1 −r max | a > π 2 ,i1∈
I}
point.Thismoduleaggregatesneighboringvoxel-wisefeatures (cid:3)
o w f it d h if a fe P r o en in t tN re e s t o [ lu 7 t ] i . o T n h s e a a n g d g a re b g s a tr t a e c d t k le e v y e p l o s in fo t r fe e a a t c u h res ke a y r p e o t i h n e t n s 10: S π 2 d , ir i 2 2 = ∈I} I 2 (cid:2) s i | 2 · , | I a 2 is = th { e i2 an | g |r le i2 d − iffe r r m e a n x | c a e ≤ and
normalizedto[0,π]
split into two paths. On the first path, these points are further
11: I ←argmax (S ,S )
down-sampled by only selecting the keypoints that are inside max {I 1 ,I 2 } dir1 dir2
the proposal B i (step (cid:4) 3 to (cid:4) 4 ) for generating CPMs. On the 12: foralli∈I max r i ←r i+π
secondpath,theyareclassifiedandselectedforlocalizationerror 13: endfor (cid:3)
correction. For the point cloud PC i, we compose the CPM i 14: s i,norm(cid:3)=s i / j s i,i,j ∈I
withthesensorposeofCAVC i,proposalsB i,coordinatesand 15: m ∗ = i b i∗ ·s (cid:3)i,norm ,∗∈{x,y,z, (cid:3) w,l,h},i∈I
featuresofkeypointsF iforfusionandK ikeypointscoordinates 16: m r =arctan2( i s i,norm ·sinr i , i s i,norm ·
forlocalizationerrorcorrection,asshowninthedash-linebox
cosr i), i∈I
inFig.2. 17: M ←M ∪{(m x ,m y ,m z ,m l ,m w ,m h ,m r)}
18: endfor
c) Fusion and detection: In the fusion step, the ego-vehicle
19: returnM
transforms all received proposal boxes and keypoints to the
same local coordinate system. The transformed proposals are
then clustered and merged using algorithm 1. If the IoU of
C. CPMCompression
two proposals in setBis above a pre-defined threshold (e.g.,
0.3), they are clustered into the same subsets C k (step 1-5). Wefollow[5]tocompresstheencodedCPMfeaturesusing
In each C k, we first align the direction r i of each BBox b i to DRACO1 inorder totake compression alsointo consideration
the dominant direction of all BBoxes in this cluster in order whencomparingtheCPMsizeofsharingoriginalfeaturemaps
topreventerroneousorientationmergingcausedbyconflicting and keypoint features. For both feature formats, we first write
BBoxdirections(step8-13).Atlast,wemergeBBoxesineach the2Dpointsoffeaturemapsorthe3DkeypointstoPLY2 file
clustertoonesingleproposalbyweighingtheBBoxparameters formatandthencompressthisfilewithDraco.
withtheirpredictionconfidences i (step14-16).Aftermerging
theBBoxesineachcluster,weendupwithKmergedproposals, D. LocalizationErrorCorrection
whicharecollectedinthesetM.
Sinceour3Dfusionmodelreliesonhighlyaccurate3Dkey-
AsshowninFig.2(c),themergedproposalsM (blackbox) points,localizationerrorwilldrasticallyreducetheperformance
arerefinedbyaggregatingtheinformationaroundthisproposal, of FPV-RCNN. To avoid this, a localization error correction
namely,theneighboringkeypoints(darkercoloredpoints)com- moduleisintroducedbeforetheBBoxmatching(Algorithm1).
ing from different CPMs (blue and orange). This aggregation Firstly, we add the semantic classification head upon the deep
is achieved by a VSA-based RoI-grid pooling module which featuresoftheselectedkeypointsasdescribedinFig.3.Then,
is originally proposed by [6]. It divides the proposal box into the keypoints are classified into classes of wall, fence, pole,
regulargridsandsummarizestheneighboringkeypointsinfor- vehicle,andothers.Basedonthesemanticclasses,weselectall
mation for each grid center. The aggregated grid features are K pointsofpolesandK pointsofwallsandfencesthrough
p fw
thenstretchedtoavectorandfedtothefullyconnectedlayers down-samplingwiththeFPS.InadditiontoC i,B iandF i,only
togeneratethefinalcooperativedetectionresultwhichcontains thex-andy-coordinateoftheselectedK i =K p +K fw points
abinaryclassificationbetweenpositiveandnegativeproposals aresharedtocorrectthelocalizationerror.Thisisdescribedin
andtheproposalboxrefinementregression.Differentto[6],we thedialogboxinFig.2asthe3rdcontentofCPM.Basedon
replaced the batch normalization (BN) [21] in the fully con- the selected keypoints of poles, fences, walls and the vehicle
nectedlayerswithdropout[22].Becauseofthecomputational
overhead of multiple point clouds in each frame, we are only
13Ddatacompression.[Online].Available:https://google.github.io/draco/
abletosetthebatchsizetooneduringtraining,whichdoesnot
2PolygonFileFormat.[Online].Available:http://paulbourke.net/dataforma
satisfytheconditionofBN. ts/ply
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore. Restrictions apply.

| 3058 |     |     |     |     |     |     |     | IEEEROBOTICSANDAUTOMATIONLETTERS,VOL.7,NO.2,APRIL2022 |     |     |     |     |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
centers,weusethemaximumconsensusalgorithm[23]witha
| rough searching |     | resolution | to  | find the | corresponding |     | vehicles |     |     |     |     |     |     |     |     |
| --------------- | --- | ---------- | --- | -------- | ------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
centersandpolespoints,andthenusethesecorrespondencesto
calculatetheaccurateerrorestimation.Wedonotusewalland
fencepointsforthefinalerrorcalculationbecausematchingon
themleadstoinaccurateresult.
|     |     | IV. | EXPERIMENTS |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
A. Dataset
Toevaluatetheperformanceoftheproposedmethod,weuse
| a synthetic | cooperative |     | perception | dataset | called   | COMAP | [9],       |     |     |     |     |     |     |     |     |
| ----------- | ----------- | --- | ---------- | ------- | -------- | ----- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| which is    | simulated   | by  | CARLA      | [24]    | and SUMO |       | [17]. Many |     |     |     |     |     |     |     |     |
Fig.4. AnoverviewofBEVdeepfeaturefusion.
| existingreal-worlddatasets,e.g., |                |           |         | KITTI[15],nuScenes[25], |                 |           |             |                    |           |               |             |     |            |         |           |
| -------------------------------- | -------------- | --------- | ------- | ----------------------- | --------------- | --------- | ----------- | ------------------ | --------- | ------------- | ----------- | --- | ---------- | ------- | --------- |
| and Waymo                        | [26],          | are more  | suited  | for                     | ego-perception, |           | whereas     |                    |           |               |             |     |            |         |           |
| collective                       | perception     | requires  |         | multiple                | CAVs            | to        | observe the |                    |           |               |             |     |            |         |           |
|                                  |                |           |         |                         |                 |           |             | that are different |           | from FPV-RCNN |             |     | are shown  | in Fig. | 4. The    |
| same scene                       | simultaneously |           |         | with enough             | FOV             | overlaps. | On          |                    |           |               |             |     |            |         |           |
|                                  |                |           |         |                         |                 |           |             | BEV features       | generated |               | by feature  |     | extraction | are     | passed to |
| the contrary,                    | the            | synthetic | dataset | containing              |                 | various   | realistic   |                    |           |               |             |     |            |         |           |
|                                  |                |           |         |                         |                 |           |             | a Spatial-Semantic |           | Feature       | Aggregation |     | (SSFA)     | [20]    | module,   |
cooperativevehiclescenarioswithaccurategroundtruthinfor- whichcanextractmorerobustfeaturesforgeneratingaccurate
| mation | is easy | to acquire | and | needs | no further | manual | work |     |     |     |     |     |     |     |     |
| ------ | ------- | ---------- | --- | ----- | ---------- | ------ | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
predictions.Thisfeaturemapisfurtherencodedandcompressed
| of data | labeling. | In addition, |     | the lack | of benchmark |     | datasets |     |     |     |     |     |     |     |     |
| ------- | --------- | ------------ | --- | -------- | ------------ | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
bytwoconvolutionallayersandthenselectedbytheproposals
| leads to | difficulty | in comparing |     | the | performance |     | of different | B   |     |     |     |     |     |     |     |
| -------- | ---------- | ------------ | --- | --- | ----------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
i.InadditiontotheselectedBEVkeypoints,theCPMsinthis
| fusion methodologies. |     |     | Hence, | in this | letter, | we follow | many |     |     |     |     |     |     |     |     |
| --------------------- | --- | --- | ------ | ------- | ------- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
casealsocontainthesensorposebutnoproposalsbecausethey
other works [4], [5], [16] to use such a synthetic dataset for arenotneededforasingle-stagedetector.Inthefusionstep,the
theempiricalstudies.
sharedfeaturemapsarefirstup-sampledtoahigherresolution
Intotal,thereare7788framesofsamplesinCOMAP—4155
|     |     |     |     |     |     |     |     | by several | transposed | convolution |     | layers | and | then | merged by |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---------- | ----------- | --- | ------ | --- | ---- | --------- |
framesfortrainingand3633framesforthetest.Eachframecon-
|     |     |     |     |     |     |     |     | a summation | of weighted |     | feature | maps. | The | weights | are auto- |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | --- | ------- | ----- | --- | ------- | --------- |
tainsthepointcloudfromanegovehicle,thepointcloudsfrom
maticallyadaptableastheyarelearnedbyaconvolutionallayer.
the cooperative vehicles in the ego vehicle’s communication Themergedfeaturemapsarethenfurtherfusedandcontracted
rangewithin40m,andthecorrespondingGTBBoxesofeach
bythreeconvolutionallayerstothedetectionresolutionforthe
| CAV. The | GT  | BBoxes | are selected |     | according | to the | detection |     |     |     |     |     |     |     |     |
| -------- | --- | ------ | ------------ | --- | --------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
finaldetection.
range57.6masthesamein[9]toguaranteeaminimumsafety
b)Baseline:Wetaketherawdatafusionstrategyasabaseline.
distanceforanemergencybrake.Forcommunicationefficiency,
Thisstrategyavoidsanydatalossduringsharing,henceismore
only up to four point clouds of the cooperative vehicles are likely to perform best. Namely, two corresponding raw data
| loaded. | To facilitate | the | feature | fusion | step, | the orientation | of  |     |     |     |     |     |     |     |     |
| ------- | ------------- | --- | ------- | ------ | ----- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
fusionnetworksaretakenasbaselines—oneforBEV-keypoints
| all the point | clouds | is  | aligned | to the | world coordinate |     | system. |               |     |       |             |     |                  |     |        |
| ------------- | ------ | --- | ------- | ------ | ---------------- | --- | ------- | ------------- | --- | ----- | ----------- | --- | ---------------- | --- | ------ |
|               |        |     |         |        |                  |     |         | fusion (noted | as  | Bbev) | and another |     | for 3D-keypoints |     | fusion |
Besides, the z-coordinates (heights) are also aligned to avoid (noted as Bfpvrcnn). Bbev takes CIA-SSD as the base object
| a big performance |     | drop | of the | object | detection | caused | by the |     |     |     |     |     |     |     |     |
| ----------------- | --- | ---- | ------ | ------ | --------- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
detector.Itsfusionframeworkisadoptedfrom[9]andispartially
| LiDARs | mounted | on  | vehicles | of different | heights. |     | After this |            |              |     |           |     |      |               |     |
| ------ | ------- | --- | -------- | ------------ | -------- | --- | ---------- | ---------- | ------------ | --- | --------- | --- | ---- | ------------- | --- |
|        |         |     |          |              |          |     |            | taken from | the FPV-RCNN |     | framework |     | that | only contains | the |
alignment,allthepointcloudsarefilteredbythedetectionrange
featureextractionandego-detectionmodule.ForBfpvrcnn,we
| on the x-y | plane | and | the height | range | [−0.1,3.9]m. |     | During |         |          |           |     |         |     |           |       |
| ---------- | ----- | --- | ---------- | ----- | ------------ | --- | ------ | ------- | -------- | --------- | --- | ------- | --- | --------- | ----- |
|            |       |     |            |       |              |     |        | add VSA | and RCNN | (RoI-grid |     | pooling | and | detection | head) |
training, the occluded GT BBoxes with no observed reflected moduletoBbevtorefinetheproposalsassimilartoFPV-RCNN
pointsareremoved.Intheend,thepre-processedpointclouds
aspossible.
arevoxelizedtoasizeof0.1mbeforetheyarefedtotheDNNs
intheframework(seeFig.2).
C. ExperimentSetup
a)Trainingsetting:Thetargetsfortrainingaregeneratedrela-
B. ComparativeModelandBaseline
tivetothepre-definedanchors.ForBbev,BEV,theegodetection
a)BEVkeypointsdeepfeaturesfusion:Sincetheworksthat ofBfpvrcnn,andFPV-RCNN,wegeneratetwoanchorsrespec-
fusedeepfeaturesmentionedinSec.IIallshareBEVfeatures, tive to rotations 0 and π/2 on each location of the 8× down-
sampledfeaturemaps.Theseanchorsareof[4.41,1.98,1.64]m
wealsobuildacomparativemodelfortheBEVfeaturefusion.
However,differentfrompreviousworks,weonlyselectfeatures in length, width, and height. An anchor is defined as positive
that are inside the proposals B for sharing to ensure a fair if its IoU against the GT BBox is over 0.6, negative if under
i
comparison between the BEV and 3D feature fusion with a 0.45,andisignoredotherwisefortheclassification.Fortheco-
similar magnitude of CPM size. We notate this framework as operativedetectionofBfpvrcnn andFPV-RCNN,wegenerate
BEV. The pipeline of BEV feature fusion is compatible with targets relative to the merged proposals by the ego detection
the one depicted in Fig. 2 a-c. The details of the modules (seeAlgorithm1).ButasingleIoUthresholdof0.3isusedto
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore.  Restrictions apply.

YUANetal.:KEYPOINTS-BASEDDEEPFEATUREFUSIONFORCOOPERATIVEVEHICLEDETECTIONOFAUTONOMOUSDRIVING 3059
separatethepositive(≥0.3)andnegative(<0.3)samples.For TABLEI
theegodetection,wesupervisethepredictionresultsofallthe
APOFDIFFERENTFUSIONMODELS(IN%)
incomingpointcloudsPC(seeSec.III-A)separately.However,
forthecooperativeperception,weonlysupervisethedetection
resultsfromtheperspectiveoftheegopointcloud.
ThesamelossfunctionsandparametersforSSDheadfrom
theoriginalwork[20]areadoptedforobjectclassification.But
positive and negative samples are weighted differently, i. e.,
50 vs. 1, to prevent the network from classifying all samples
asnegative.FortheRCNNhead,abinarycross-entropylossis
usedforclassificationandasmoothL1-lossforregression.They
arenormalizedoverallsamples.SincetheCAVsalsosharetheir
ownposeswitheachother,wealsoaddtheGTBBoxesoftheego
vehicleandalltheselectedcooperativevehiclestothedetection for the global localization error of both ego and cooperative
beforefeedingthemtotheNon-Maximum-Suppression(NMS). vehicles:N(0,0.42)minx-andy-directionandN(0,42)◦ for
ThethresholdsfortheclassificationscoresandtheNMSIoUs theorientationofthevehicles.Thiswillleadtomuchlargerrela-
aresetto0.3and0.01,respectively,andkeptthesameinthetest tiveerrors.Accordingtotheerrorstandarddeviation,thesearch
phase.
rangeofmaximumconsensusisempiricallysetto[−1,1]mfor
We run all the experiments only on a single Nvidia 1080Ti x- and y-axis and [−6,6]◦ for the orientation. The searching
GPUtosimulatearestrictedcomputationalresourceinanAV.
resolutionissetto1mand1◦forthetranslationandorientation,
Bbevistrainedfromscratchfor50epochswithabatchsizeof8 respectively.
frames.Thetrainedweightsareusedforinitializingtheweights c) Evaluation metrics: All results are evaluated by Average
ofthefeatureextractionandegodetectionmoduleinBfpvrcnn, Precision (AP) defined by the Area Under Precision-Recall
BEV,FPV-RCNN.Thesethreenetworksarethenfurtherfine- Curve. IoU criteria (0.3,0.5,0.7) are used for counting the
tunedfor10epochswithabatchsizeof4forBfpvrcnnand1for positivedetectiontoevaluatethedetectionperformance.
theothertwo.TheAdamoptimizer(coefficientsof0.95&0.999)
isappliedtooptimizethelossesbystochasticgradientdescent. V. RESULTANDEVALUATION
Its learning rate and decay both are set to 1e−4. We provide
A. ComparisonWithBaselines
thedetailedsettingsinourhttps://github.com/YuanYunshuang/
FPV_RCNNrepositoryforreproducingourmodels. Table I shows the AP scores of the baselines (in the gray
b)Testsetting:Differentnumbersofcooperativevehiclesare cell)andthefusionmodels.Withcooperativevehicles(N >0),
v
testedforanalyzingtheperformanceofcooperativeperception. comparedtotheBbevandBfpvrcnnfusionbaselines(boldfontin
This is done by fixing the number of cooperative vehicles N thegraycell),BEV-fusionhasanacceptablesmallperformance
v
ineachtestrun.Namely,N variesfrom0,2to4.Ineachrun, drop at the low IoU threshold (0.3). It is worth noting that the
v
onlytheframeshavingatleastN
v
cooperativepointcloudsare performance of FPV-RCNN even surpasses that of Bfpvrcnn
selected as a test set for evaluation. If there are more than N with a small AP gain at different IoUs. For example, when
v
cooperativepointclouds,werandomlyselectN outofthemto there are only two cooperative vehicles, the AP of BEV at
v
simulatetherandomgeometricdistributionofCAVs. IoU=0.3drops0.72%whilethatof3D-fusionevenincreases
Moreover, different CPM feature channels are analyzed for 0.43%, compared to their respective baselines. However, as
the keypoints feature fusion. We set CPM feature channels to the IoU threshold increases to 0.5, the gap between BEV and
128 to compare with both the BEV and 3D keypoints fusions Bbev slightly increases. At IoU=0.7, the gap between them
under the condition of no information loss during the CPM evenincreasesto8.34%.Incontrast,theperformanceofFPV-
compression process. To further investigate the possibility of RCNN is slightly better than its baseline Bfpvrcnn, and their
decreasingthesizeofCPMsintheFPV-RCNNframework,we performancegapsaresmallandremainconsistent.Thisimplies
conductaseriesofexperimentsbysettingdifferentN forFPS that the additional RCNN-head helps improve the localization
kpts
(2048and1024)anddifferentCPMfeatureencodingchannels accuracy of the BBoxes at lower IoU thresholds, but not the
N (128,64,and32). recalloftheBBoxes.ThisisbecausetheRoI-gridpoolingcan
ch
Maximum consensus algorithm is very stable against the better aggregate the 3D keypoints features learned from the
magnitudeofthenoise—differentnoisedistributionsonlylead pointcloudforhighaccurateBBoxpredictions.Inotherwords,
to a change in the search range of the maximum consensus comparedtoBEV,ourmodelismoresuitableforfeaturefusion
algorithm.Therefore,weonlyuseonefixednormaldistribution ofcooperativeobjectdetectionwithrespecttohighlyaccurate
fortheabsolutelocalizationerrorofeachvehicletoinvestigate andreliableBBoxpredictions.
the influence of pose errors on the fusion framework. This is Nevertheless, when there are no cooperative vehicles, our
different from [5] which imports errors to the relative pose FPV-RCNNperformsmuchworsethantheothertwobaselines.
between ego and cooperative vehicles and vary the translation Thisisbecausetheseself-dependentdetectionresultsaregen-
error from 0 to 0.4m, the rotation error from 0 to 4◦. In our eratedonlybythefeatureextractionandego-detectionmodule.
experimentweonlyusethebiggesterrorsettingfromtheirwork The weights of these two modules are fine-tuned during the
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore. Restrictions apply.

3060 IEEEROBOTICSANDAUTOMATIONLETTERS,VOL.7,NO.2,APRIL2022
TABLEII TABLEIII
PERFORMANCEOFFPV-RCNNWITHDIFFERENTNUMBEROFKEYPOINTSAND ABLATIONSTUDYWITHANDWITHOUTNOISE(APIN%)
CPMENCODINGCHANNELS(APIN%)
less data than the BEV keypoints fusion but achieves an en-
hancedperformancebyabigmargin(90.88%vs.82.21%,see
TableI).Besides,ourframeworkalsogeneratesCPMswithsizes
inthesameorderofmagnitudeastheobject-basedstandardized
CPM[27]evaluatedinalowtrafficdensityscenarioby[28].
Theseobservations above indicatethatourproposedframe-
workisrelativelystableagainstthevariationoftheCPMfeature
encodingsize.Hence,ifthecommunicationnetworkisnotfully
consumedandthewirelessnetworkcanhandlelargerCPMs,it
Fig.5. CPMsizecomparison. is preferable to increase N rather than increase the feature
kpts
encoding channels. On the other hand, as a big advantage,
if the communication network is already heavily loaded, the
training of the whole BEV and 3D fusion framework. This CPMscanbecompressedassmallaspossiblewithonlyaslight
observationindicatesthatBEVtendstolearnfeaturesthatare performancedrop.
morehelpfulfordetectiontasksonasinglepointcloud.Thus,it
overfitsundersuchaconfigurationwithbetterperformancethan
C. AblationStudyWithRespecttoLocalizationNoise
that of the more generalized Bbev (e. g., 61.59% vs. 57.98%
at IoU=0.7). In contrast, FPV-RCNN focuses on learning Inordertoshowtheeffectivenessofthematchingmodulewe
features that are useful for the later fusion, and therefore are proposedinAlgorithm1,wecomparetheresultofthismodule
counter-affected by the original pre-trained weights for non- with the NMS object fusion used in V2Vnet [5]. As shown in
cooperativedetection.Itshouldbenotedthatthisissuecanbe theboldfontinTableIII,ourmatchingmoduleoutperformsthe
circumventedbyloadingdifferentpre-trainedweightsaccording NMSfusioninmostofthecases.Especially,whenlocalization
totherequirementsinrealapplications. noise exists, matching using Algorithm 1 is more stable. In
addition,wealsostudiedtheperformancegainofthe3Dfeature
fusionofFPV-RCNNinthesecondstage.Thebest-performed
B. FPV-RCNNPerformanceWithVariateCPMSizes
resultsaremarkedinblue,whichclearlyindicatesthatourfusion
TableIIshowstheresultsofFPV-RCNNwithdifferentCPM module of FPV-RCNN can refine the results. Moreover, by
encodingparameters.N standsforthenumberofkeypoints observingthedetectionresults,wefoundthatmostofthefalse
kpts
forFPSandN standsforthenumberofchannelsforencod- positivedetectionisremovedbyRCNNinthesecond3Dfeature
ch
ing the CPM features. Besides, the results are evaluated with fusionstage.However,thiseffectcanhardlyinfluencetheresult
two different numbers of cooperative vehicles (N ={2,4}). of AP. Therefore, we do not observe large AP improvement
v
In general, the better performance is mostly associated with a between the results of the full FPV-RCNN and Algorithm 1.
largerN andallbestAPscores(boldbluefont)appearwhen Moreover,asshowninTableIII,our3Dmodelwithlocalization
kpts
N =2048. But for a specific IoU and N , the performance noise, as expected, performs worse than the no-noise version.
v v
only varies within a range of less than 1% for different N . But the performance at lower IoU thresholds is only slightly
ch
Interestingly, in most cases, the best AP even appears at the dropped.However,asshowninFig.6,withlocalizationnoise,
smallestN (boldfont). our3DmodelstillperformsbetterthantheBEVfusionmodel.
ch
Furthermore,wecomparetheCPMsizesofthecompressed Since the raw data fusion baselines do not have the keypoints
deepfeaturesaveragedoverallCPMsandCAVnumbers.Fig.5 selection and classification module, it is difficult to correct
gives a quantitative comparison between BEV and 3D (FPV- localizationerrorandtheirresultsarenotplottedinFig.6.
RCNN,notedwithadifferentN )keypointsfeaturesharing. Nevertheless,thecurrentmodelalsohasseverallimitations.
kpts
It can be seen that the average CPM size of the compressed First,weonlycarriedouttheempiricalstudiesonthesynthetic
keypoints features is decreased to around 0.3 KB, which is data.Inourfuturework,firstwewillextendourexperimentto
about50timessmallerthantheCPMgeneratedbycompressing real-world data to further analyze the efficacy of the proposed
the whole feature maps (ca. 14 KB). With the same number FPV-RCNN model. Second, the communication delay is only
offeaturechannels(N =128),3Dkeypointsfusiontransmits reflectedbytheCPMsizes.Thisneedstobefurtherinvestigated
ch
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore. Restrictions apply.

YUANetal.:KEYPOINTS-BASEDDEEPFEATUREFUSIONFORCOOPERATIVEVEHICLEDETECTIONOFAUTONOMOUSDRIVING 3061
|     |     |     |     |     |     |     | [7] C.R.Qi,H.Su,K.Mo,andL.J.Guibas,“Pointnet:Deeplearningon |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
pointsetsfor3Dclassificationandsegmentation,”inProc.IEEEConf.
Comput.Vis.PatternRecognit.,2017,pp.77–85.
|     |     |     |     |     |     |     | [8] C.R.Qi,L.Yi,H.Su,andL.J.Guibas,“Pointnet:Deephierarchicalfeature |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
learningonpointsetsinametricspace,”inAdv.NeuralInf.Process.Syst.,
2017,pp.5099–5108.
|     |     |     |     |     |     |     | [9] Y. Yuan | and M.     | Sester, “COMAP: |            | A synthetic    | dataset for      | collective |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --------------- | ---------- | -------------- | ---------------- | ---------- |
|     |     |     |     |     |     |     | multi-agent | perception | of              | autonomous | driving,” Int. | Arch. Photogram- |            |
metry,RemoteSens.SpatialInf.Sci.,vol.XLIII-B2-2021,pp.255–263,
2021.
|     |     |     |     |     |     |     | [10] S.Yangetal.,“COSMOSsmartintersection:Edgecomputeandcom- |            |         |           |                     |             |            |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------------ | ---------- | ------- | --------- | ------------------- | ----------- | ---------- |
|     |     |     |     |     |     |     | munications                                                  | for bird’s | eye     | object    | tracking,” in Proc. | IEEE        | Int. Conf. |
|     |     |     |     |     |     |     | Pervasive                                                    | Comput.    | Commun. | Workshops | (PerCom             | Workshops), | 2020,      |
pp.1–7.
|     |     |     |     |     |     |     | [11] T.Niels,N.Mitrovic,K.Bogenberger,A.Stevanovic,andR.L.Bertini, |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------------------ | --- | --- | --- | --- | --- | --- |
Fig.6. Resultswithlocalizationerrors.
“Smartintersectionmanagementforconnectedandautomatedvehicles
andpedestrians,”inProc.6thInt.Conf.ModelsTechnol.Intell.Transp.
Syst.,2019,pp.1–10.
byanalyzingtheCPMcommunicationandtransmissioninreal- [12] C. Allig and G. Wanielik, “Alignment of perception information for
|     |     |     |     |     |     |     | cooperative | perception,” | in  | Proc. | IEEE Intell. Veh. | Symp. | (IV), 2019, |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------------ | --- | ----- | ----------------- | ----- | ----------- |
worldscenarios.
pp.1849–1854.
|     |     |     |     |     |     |     | [13] A.Miller,K.Rim,P.Chopra,P.Kelkar,andM.Likhachev,“Cooperative |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
VI. CONCLUSION perceptionandlocalizationforcooperativedriving,”inProc.IEEEInt.
Conf.Robot.Automat.,2020,pp.1256–1262.
In this letter, we proposed an efficient framework, called [14] Q.Chen,S.Tang,Q.Yang,andS.Fu,“Cooper:Cooperativeperception
forconnectedautonomousvehiclesbasedon3Dpointclouds,”inProc.
| FPV-RCNN, | for | point cloud-based | cooperative |     | vehicle | detec- |     |     |     |     |     |     |     |
| --------- | --- | ----------------- | ----------- | --- | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
IEEE39thInt.Conf.Distrib.Comput.Syst.,2019,pp.514–524.
tionofautonomousdriving.TheframeworktakesPV-RCNN[6]
|             |         |           |           |                 |     |      | [15] A.Geiger,P.Lenz,andR.Urtasun,“Arewereadyforautonomousdriving? |        |           |         |               |               |      |
| ----------- | ------- | --------- | --------- | --------------- | --- | ---- | ------------------------------------------------------------------ | ------ | --------- | ------- | ------------- | ------------- | ---- |
| as the base | network | of object | detection | for cooperative |     | per- |                                                                    |        |           |         |               |               |      |
|             |         |           |           |                 |     |      | the KITTI                                                          | vision | benchmark | suite,” | in Proc. IEEE | Conf. Comput. | Vis. |
PatternRecognit.,2012,pp.3354–3361.
| ception | scenarios | by adding | a keypoints | selection | module, |     | a                                                                    |     |     |     |     |     |     |
| ------- | --------- | --------- | ----------- | --------- | ------- | --- | -------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|         |           |           |             |           |         |     | [16] S.Manivasagametal.,“LiDARsim:Realisticlidarsimulationbyleverag- |     |     |     |     |     |     |
boundingboxproposalmatchingmodulewithlocalizationerror
ingtherealworld,”inProc.IEEEConf.Comput.Vis.PatternRecognit.,
correction, and the keypoints fusion module. The comparison 2020,pp.11164–11173.
P.A.Lopezetal.,“MicroscopictrafficsimulationusingSUMO,”inProc.
| toa2DBEVfeaturefusiononasimulateddatasetCOMAP[9] |     |     |     |     |     |     | [17] |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
21stInt.Conf.Intell.Transp.Syst.,2018,pp.2575–2582.
showsthatourmethodimprovestheperformanceofcooperative
|     |     |     |     |     |     |     | [18] B. Graham, | “Sparse | 3D convolutional |     | neural networks,” | in  | Proc. Brit. |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ------- | ---------------- | --- | ----------------- | --- | ----------- |
vehicle detection by a big margin. In comparison to previous Mach.Vis.Conf.,BMVAPress,2015,pp.150.1-150.9.
worksthatsharefullBEVfeaturemaps,ourmethodsignificantly [19] B.Graham,M.Engelcke,andL.vanderMaaten,“3DSemanticsegmen-
|     |     |     |     |     |     |     | tationwithsubmanifoldsparse |     |     | convolutionalnetworks,” |     | inProc. | 2018 |
| --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | ----------------------- | --- | ------- | ---- |
decreasesthedatatransmissionloadintheCAVnetworkforreal- IEEE/CVFConf.Comput.Vis.Patt.Recognit.,2018,pp.9224–9232.
timecommunicationandisalsomorerobustagainstlocalization [20] W.Zheng,W.Tang,S.Chen,L.Jiang,andC.Fu,“CIA-SSD:Confident
noisethankstothenoisecorrectionmodule.Infuturework,we iou-awaresingle-stageobjectdetectorfrompointcloud,”inProc.AAAI
Conf.Artif.Intell.,AAAIPress,2021,pp.3555–3562.
plan to evaluate our method in real-world cooperative driving [21] S.IoffeandC.Szegedy,“Batchnormalization:Acceleratingdeepnetwork
scenarios. training by reducing internal covariate shift,” in Proc. 32nd Int. Conf.
Mach.Learn.,2015,vol.37,pp.448–456.
|     |     |     |     |     |     |     | [22] N.Srivastava,G.E.Hinton,A.Krizhevsky,I.Sutskever,andR.Salakhutdi- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
REFERENCES
nov,“Dropout:Asimplewaytopreventneuralnetworksfromoverfitting,”
J.Mach.Learn.Res.,vol.15,no.1,pp.1929–1958,2014.
[1] C.Premebida,R.Ambrus,andZ.-C.Marton,“Intelligentroboticpercep-
|     |     |     |     |     |     |     | [23] T.ChinandD.Suter,TheMaximumConsensusProblem:RecentAlgorith- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
tionsystems,”Appl.MobileRobots,2019,pp.111–127,doi:10.5772/in-
micAdvances(SynthesisLecturesonComputerVisionSeries).Morgan
techopen.79742.
&ClaypoolPublishers,2017.
[2] M.Shanetal.,“Demonstrationsofcooperativeperception:Safetyandro-
|     |     |     |     |     |     |     | [24] A. Dosovitskiy, | G.  | Ros, | F. Codevilla, | A. M. López, | and | V. Koltun, |
| --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | ---- | ------------- | ------------ | --- | ---------- |
bustnessinconnectedandautomatedvehicleoperations,”Sensors(Basel, “CARLA: An open urban driving simulator,” in Proc. 1st Annu. Conf.
Switzerland),vol.21,no.1,2021,Art.no.200.
RobotLearn.,2017,vol.78,pp.1–16.
[3] Q.Chen,X.Ma,S.Tang,J.Guo,Q.Yang,andS.Fu,“F-cooper:Feature
|        |             |                   |                |              |       |           | [25] H.Caesaretal.,“Nuscenes:Amultimodaldatasetforautonomousdriv- |                |     |               |              |            |       |
| ------ | ----------- | ----------------- | -------------- | ------------ | ----- | --------- | ----------------------------------------------------------------- | -------------- | --- | ------------- | ------------ | ---------- | ----- |
| based  | cooperative | perception        | for autonomous | vehicle      | edge  | computing |                                                                   |                |     |               |              |            |       |
|        |             |                   |                |              |       |           | ing,” in                                                          | Proc. IEEE/CVF |     | Conf. Comput. | Vis. Pattern | Recognit., | 2020, |
| system | using       | 3D point clouds,” | in Proc.       | 4th ACM/IEEE | Symp. | Edge      |                                                                   |                |     |               |              |            |       |
pp.11618–11628.
Comput.,2019,pp.88–100. [26] P.Sunetal.,“Scalabilityinperceptionforautonomousdriving:Waymo
[4] E.E.Marvasti,A.Raftari,A.E.Marvasti,Y.P.Fallah,R.Guo,andH.Lu,
opendataset,”inProc.IEEEConf.Comput.Vis.PatternRecognit.,2020,
“Featuresharingandintegrationforcooperativecognitionandperception
pp.2443–2451.
withvolumetricsensors,”2020,arXiv:2011.08317.
|           |       |                 |           |          |          |     | [27] “Intelligenttransportsystem(ITS);Vehicularcommunications;Basicset |     |     |     |     |     |     |
| --------- | ----- | --------------- | --------- | -------- | -------- | --- | ---------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| [5] T.-H. | Wang, | S. Manivasagam, | M. Liang, | B. Yang, | W. Zeng, | and |                                                                        |     |     |     |     |     |     |
ofapplications,”Anal.CollectivePercep.Service(CPS);Release2,Tech.
R. Urtasun, “V2VNet: Vehicle-to-vehicle communicationfor jointper- Rep.ETSITR103562,2020.Accessed:31Aug.2021.[Online].Avail-
ceptionandprediction,”inProc.16thEur.Conf,Comput.Vis.-ECCV
able:https://www.etsi.org/deliver/etsi_tr/103500_103599/103562/02.01.
2020,PartII,Springer,2020,vol.12347,pp.605–621.
01_60/tr_103562v020101p.pdf
[6] S.Shietal.,“PV-RCNN:Point-voxelfeaturesetabstractionfor3Dobject
|     |     |     |     |     |     |     | [28] F.A.Schiegg,I.Llatser,D.Bischoff,andG.Volk,“Collectiveperception: |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2020, Asafetyperspective,”Sensors,vol.21,no.1,2021,Art.no.159.
pp.10526–10535.
Authorized licensed use limited to: San Jose State University. Downloaded on September 02,2026 at 03:33:03 UTC from IEEE Xplore.  Restrictions apply.