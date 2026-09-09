| Before |     | Fusion,    | Ask | What       | to Keep:            | Contextual |     | Calibration  |     | of  |
| ------ | --- | ---------- | --- | ---------- | ------------------- | ---------- | --- | ------------ | --- | --- |
|        |     |            |     | Multimodal |                     | Signals    |     |              |     |     |
|        |     | JiyuanLiu∗ |     |            | LiangweiNathanZheng |            |     | WeiEmmaZhang |     |     |
jiyuan.liu@student.adelaide.edu.au liangwei.zheng@adelaide.edu.au wei.e.zhang@adelaide.edu.au
|     | AdelaideUniversity |     |     |     | AdelaideUniversity |     |     | AdelaideUniversity |     |     |
| --- | ------------------ | --- | --- | --- | ------------------ | --- | --- | ------------------ | --- | --- |
|     | Adelaide,Australia |     |     |     | Adelaide,Australia |     |     | Adelaide,Australia |     |     |
WeitongChen∗
XinpeiWang
|     |     |     | wangxinpei@sdu.edu.cn |     |     | T.Chen@Adelaide.edu.au |     |     |     |     |
| --- | --- | --- | --------------------- | --- | --- | ---------------------- | --- | --- | --- | --- |
|     |     |     | ShandongUniversity    |     |     | AdelaideUniversity     |     |     |     |     |
|     |     |     | Jinan,China           |     |     | Adelaide,Australia     |     |     |     |     |
6202 nuJ 1  ]GL.sc[  1v97620.6062:viXra
Abstract under-optimized[9].Thisproblembecomesmorechallengingwhen
weakorlessreliablemodalitiesmayintroducenoisy,redundant,or
| Multimodal | systems | often | benefit from | combining | information |     |     |     |     |     |
| ---------- | ------- | ----- | ------------ | --------- | ----------- | --- | --- | --- | --- | --- |
conflictinginformationintomultimodallearning[32].Therefore,
acrosslanguage,sound,andvisualstreams,butthisbenefitisnot
guaranteed.Amodalitythatisusefulforoneinputmaybecome less reliable modalities may still provide useful complementary
distractingforanother,andlocalfeatureresponseswithinthesame cues,buttheymayalsocontainharmfulorconflictingcomponents
thatinterferewithfull-modalitypredictionwhendirectlyfused
modalitycandisagreewithevidencefromothersources.Thiswork
intothebackbone.
investigateshowtoadjustmultimodalrepresentationsbeforethey
Existingstudiesmainlyaddressthisissuefromanoptimization-
| are merged | by a | downstream | predictor. | We develop | a compact |     |     |     |     |     |
| ---------- | ---- | ---------- | ---------- | ---------- | --------- | --- | --- | --- | --- | --- |
calibrationmodulethatcompareseachmodalitywiththeothers levelmodalityimbalanceperspective.MethodssuchasGrad-Blending,
atthesummarylevel,extractscuesofcross-sourcesupportand OGM-GE,PMR,MMPareto,andARLimprovemultimodallearning
conflict,andconvertsthesecuesintoinstance-wiseanddimension- byadjustinglosses,gradients,modalitycontributions,orrepresen-
tationlearningdynamics[2,9,19–21,28].Althougheffective,these
wisemodulationsignals.Thecalibrationisappliedtotheoriginal
|     |     |     |     |     |     | methods mostly | intervene | after modality | features | have entered |
| --- | --- | --- | --- | --- | --- | -------------- | --------- | -------------- | -------- | ------------ |
modalityfeaturesratherthantoalreadyfusedrepresentations,en-
abling the model to suppress misleading components, preserve jointoptimization.Theythereforedonotfullyansweranearlier
weakbutusefulevidence,andemphasizeresponsesthatarebet- question:beforemultimodalfusion,howcanamodelidentify
tersupportedbythecurrentmultimodalcontext.Themoduleis contextuallyinfluentialbutpotentiallyunreliablemodality
componentsanddecidewhethertheyshouldbeenhanced,
designedasaplug-incomponentandcanbeattachedtodifferentfu-
retained,orsuppressed?
sionbackboneswithoutchangingtheirpredictionheads.Acrossfive
Thisquestionisimportantbecausedirectfusioncanmixuseful
benchmarkscoveringsentimentunderstanding,actionrecognition,
audio-visualeventdetection,andaudio-visualemotionclassifica- evidencewithunreliablesignalsbeforethemodelhasanexplicit
tion,theproposedpre-combinationcalibrationstrategyimproves chancetodistinguishthem.Thismotivatesvalueestimationasa
mechanismforguidingmodalityrefinementatthepre-fusionstage.
performanceunderbothsequence-basedandconvolutionalfusion
settings.Additionalanalysesundermodalityremoval,synthetic
corruption,trainingdynamics,andfeature-levelvisualizationshow
|     |     |     |     |     |     | Table 1: Preliminary |     | comparison | between | naive fusion, |
| --- | --- | --- | --- | --- | --- | -------------------- | --- | ---------- | ------- | ------------- |
thatcalibratingsignalsbeforefusioncanreduceinterferencefrom
optimization-levelbalancing,andenhancedpre-fusiontrans-
unreliablemodalitiesandproducemorestablemultimodalopti-
formationonMOSEI.
mization.
|     |     |     |     |     |     |     | Method | Acc | Macro-F1 |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | --- | -------- | --- |
1 Introduction
|     |     |     |     |     |     |     | Concat | 0.8255 | 0.7810 |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ------ | ------ | --- |
Multimodal learning aims to improve prediction by integrating MMPareto 0.8279 0.7812
heterogeneoussignalsfromdifferentmodalities,suchastext,vi- Concat+MLP 0.8298 0.7803
sion,knowledgegraph,anddomain-specificsignals[12–14,25].In
principle,differentmodalitiesprovidecomplementaryviewsofthe
sameevent,andmultimodalfusionhasbeenwidelyusedtomodel As shown in Table 1, simple concatenation performs poorly,
intra-modalandinter-modaldynamics[16,25].However,adding whileConcat+MLPreachesaperformancerangecomparableto
moremodalitiesdoesnotalwaysimproveperformance.Priorwork MMPareto.Thissuggeststhatlightweightpre-fusiontransforma-
showsthatmultimodalnetworksmayunderperformunimodalmod- tioncanpartiallymitigatemodalityinterferencebeforejointopti-
mization.However,Concat+MLPstillperformsagenericfeature
elsbecausedifferentmodalitiesoverfitandgeneralizeatdifferent
rates[19].Modalityimbalancecanalsocausedominantmodalities transformationanddoesnotexplicitlyestimatewhichmodality
tosuppressweakerones,leavingsomeunimodalrepresentations componentsarecontextuallyinfluentialundercross-modalagree-
mentordiscrepancy.Thismotivatesourvalue-awarepre-fusion
| ∗Correspondingauthors. |     |     |     |     |     | refinementdesign. |     |     |     |     |
| ---------------------- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- |

JiyuanLiu,LiangweiNathanZheng,WeiEmmaZhang,XinpeiWang,andWeitongChen
Inthispaper,wedefinemodalityvalueascontext-conditioned Grad-Blendingaddressesmultimodalimbalancefromtheper-
impactevidenceformultimodalprediction.Ratherthanserving spectiveofoverfittingandgeneralizationdifferencesacrossmodal-
asadirectretentionprobability,valueindicateswherestronger ities[19].OGM-GEdynamicallymeasurescontributiondiscrep-
context-aware modulation may be needed, while the final gate ancybetweenmodalitiesandmodulatesgradientstogivemore
learnswhethereachcomponentshouldbeenhanced,retained,or optimizationefforttounder-optimizedmodalities[9].PMRintro-
reduced. ducesmodalityprototypestostimulateslow-learningmodalities
Attention-based methods mainly model token-level or cross- andrebalancetheirlearningprogress[2],whileAGMadaptively
modalrelevance[16,17],whilegenericgatingmechanismsusually adjustsmodalitygradientsaccordingtoestimatedmodalitycon-
learn adaptive feature or modality weights [6, 8]. Recent multi- tribution[7].MMParetoformulatesmultimodalandunimodalob-
modalgatingmethodsfurtherexploreconfidence-guidedgating jectivesfromaParetooptimizationperspectivetoreducegradient
forflexibleorincompletemodalityinputs[31].However,relevance, conflict[21].D&Rdiagnosesthelearningstateofeachmodalityand
confidence,orimportancedoesnotnecessarilyindicatevalueinour re-learnsmodalityencoderstoavoidover-emphasizingscarcely
setting,becauseasalientorconfidentmodalitycanstillbeharmful informativemodalities[22].MLAreformulatesjointmultimodal
whenitconflictswiththecurrentcross-modalcontext. trainingasalternatingunimodaladaptation,reducinginterference
Basedonthisdefinition,weproposeValue-GatedModalityRe- whilemaintainingsharedprediction[30].ARLfurtherarguesthat
finer(VGMR),apre-fusionrefinementmoduleforrobustmulti- perfectlybalancedmodalitylearningisnotalwaysoptimal,and
modallearning.VGMRfirstmodelssummary-levelcross-modal uses asymmetric representation learning according to modality
interactionsbycapturingbothagreementanddiscrepancybetween varianceandbias[20].
thetargetmodalityandtheremainingmodalities.Itthenestimates Overall,thesemethodsshowthatmultimodalimbalanceisclosely
valuesignalsatboththeglobalandchannellevels,andusesthese relatedtounequallearningdynamicsamongmodalities.However,
signalsascontextualguidanceforafine-grainedgategeneratorthat theymainlyinterveneduringjointtrainingbyadjustinglosses,
refinestheoriginalmodalityfeaturesbeforetheyentertheback- gradients,modalityweights,orrepresentationlearningstrategies.
bone.Bydoingso,VGMRallowsthemodeltopreserve,enhance,or Incontrast,thisworkstudieswhethernoisyorunreliablemodality
reducemodalitycomponentsaccordingtobothcross-modalvalue responsecomponentscanberefinedbeforetheyenterfusionor
evidenceandfeature-levelcontextbeforefusion. jointoptimization.
We conduct extensive experiments and analyses to examine
whetherVGMRimprovesmultimodallearningbeyondsimplefea-
2.2 MultimodalFusionandCross-Modal
tureaggregation,genericgating,ortraining-stagerebalancing.The
Interaction
resultsshowthatpre-fusionvalue-conditionedrefinementcanim-
prove multimodal performance, enhance robustness under cor- Multimodalfusionaimstocombineheterogeneousmodalityfea-
ruptedinputs,andsupportmorestableoptimizationbehaviour. turesandexploitcomplementaryinformationacrossmodalities.
Themaincontributionsofthispaperaresummarizedasfollows: Earlyfusionmethodsaggregatemodalityrepresentationsthrough
summation,concatenation,orMLP-basedfusion,whilemoreex-
• Werevisitmultimodalimbalancefromapre-fusionperspec- pressivemethodsmodelhigher-ordercross-modalinteractions.For
tive,highlightingthatweakmodalitiesmaycontainboth example,TensorFusionNetworkexplicitlycapturesunimodal,bi-
complementarycuesandnoisyorharmfulresponses. modal,andtrimodalinteractions[25],andTransformer-basedmulti-
• WeproposeVGMR,avalue-conditionedmodalityrefiner modalmodelsuseattentionmechanismstocapturelong-rangeand
thatestimatesglobal-levelandchannel-levelimpactevi- cross-modaldependencies[16,17].Multimodalfusionhasalsobeen
denceandusesittoguidefine-grainedgatingoveroriginal widelystudiedindomain-specificapplications,includingmedical
modalityfeaturesbeforefusion. multimodallearning[12].
• Weconductextensiveexperimentsanddiagnosticanalyses Recentstudiesfurthershowthateffectivefusionrequiresmore
to show that VGMR improves multimodal performance, thandirectaggregation.MISAlearnsmodality-invariantandmodality-
enhancesrobustnessundernoisyinputs,andsupportsmore specificsubspacestoreducemodalitygapswhilepreservingpri-
stableoptimizationbehaviour. vatemodalitycharacteristics[5].MAGintroducesamultimodal
adaptationgatetoinjectacousticandvisualinformationintopre-
trainedlanguagemodels[10].MMIMimprovesfusionbymaxi-
2 RelatedWork mizingmutualinformationatboththeinter-modalityleveland
thefusion-outputlevel[3].Self-MMlearnsmodality-specificrepre-
2.1 ModalityImbalanceandOptimization
sentationsthroughself-supervisedunimodallabelgeneration[24].
Balancing
TETFNenhancesnon-linguisticmodalitieswithtext-basedatten-
Modalityimbalanceisacommonchallengeinmultimodallearn- tionandlearnsbothconsistencyanddifferentiatedinformation
ing,wheredifferentmodalitiescontributeunequallyduringjoint acrossmodalities[18].PCAGintroducespre-gatingandcontextual
training.Adominantmodalitymaysuppressweakermodalities, attentiongatestofilternon-informativecross-modalinteractions
andaddingmoremodalitiesdoesnotalwaysimproveprediction. andreduceuncertaintyintroducedbycross-attention[29].
Existingmethodsmainlyaddressthisissuebyadjustingmodality Thesestudiesshowthatmultimodalfusionhasevolvedfrom
contributionsduringtraining,includinglossbalancing,gradient simpleaggregationtoexpressivealignment,interaction,informa-
modulation,modalityreweighting,andrepresentationre-learning. tionpreservation,andgating-basedmechanisms.However,most

BeforeFusion,AskWhattoKeep:ContextualCalibrationofMultimodalSignals
fusion-orientedmethodsfocusonhowtocombine,align,orinteract 3 ProposedMethod
modalityrepresentations.Evenwhenattentionorgatingisused,
3.1 ProblemDefinition
thelearnedweightsusuallyreflectrelevance,salience,confidence,
TheoverallarchitectureofVGMRisshowninFigure1.Givena
or feature importance. They do not explicitly estimate context-
multimodalsamplewithmodalitysetM,eachmodalityisindexed
conditionedvalueevidenceforrefiningoriginalmodalityfeatures
by𝑚∈M.Fortext-audio-visiontasks,M ={𝑡,𝑎,𝑣};forbimodal
beforefusion.
tasks,Mcontainsthetwoavailablemodalities,suchas{𝑎,𝑣}.
Foreachmodality𝑚,theinputfeaturesequenceisdenotedas
X𝑚
∈R𝑇𝑚×𝑑𝑚,
(1)
2.3 InformationDecompositionPerspective
where𝑇 𝑚 and𝑑 𝑚 arethemodality-specificsequencelengthand
Thisissueisalsorelatedtotheinformation-decompositionper- featuredimension,respectively.VGMRaimstorefineeachmodality
spective. Partial Information Decomposition (PID) provides an beforefusionbyestimatingcontext-conditionedvaluesignalsand
information-theoreticviewforunderstandinghowmultiplesources usingthemtoguidegategeneration.Ittakes{X𝑚}𝑚∈M asinput
contributetoatargetvariablebyseparatingredundant,unique,and andoutputsrefinedfeatures{X˜ 𝑚}𝑚∈M,whicharethenfedinto
synergisticinformation[23].Thisperspectiveisusefulformulti- themultimodalbackbone.
modallearningbecausethecontributionofamodalitycannotbe
fullydescribedbyasingleimportancescore.Amodalitymaycon- 3.2 ModalityProjectionandSummary
tainredundantinformationsharedwithothermodalities,unique Construction
informationfromitself,orsynergisticinformationthatbecomes
Sincedifferentmodalitieshavedifferentfeaturedimensions,each
usefulonlywhencombinedwithothermodalities.
modalityisfirstprojectedintoasharedlatentspace:
Ourmethodisconceptuallyinspiredbythisview,butitdoesnot
aimtoexplicitlyestimatePIDquantities.Instead,PIDmotivatesus H𝑚 =𝑃 𝑚(X𝑚), H𝑚 ∈R𝑇𝑚×𝑑𝑝, (2)
toconsiderthatmodalitycomponentsmayhavedifferentcontex-
where𝑃 𝑚(·) isamodality-specificprojectionfunctionand𝑑 𝑝 is
tualeffectsundercross-modalagreementanddiscrepancy.VGMR
thesharedlatentdimension.TheprojectedfeatureH𝑚isusedfor
operationalizesthisintuitionthroughlearnableglobal-leveland
valueestimation,whiletheoriginalfeatureX𝑚 ispreservedfor
channel-levelvalueestimation,allowingusefulmodality-specificor
finalrefinement.
complementaryinformationtobepreservedwhilenoisyorharmful
Wethenconstructasummaryrepresentationforeachmodality
componentsarereducedbeforefusion.
bycombiningaverageandmaxpooling:
s𝑚 =𝜙 𝑚([Avg(H𝑚);Max(H𝑚)]), s𝑚 ∈R𝑑𝑝, (3)
where[·;·]denotesconcatenationand𝜙 𝑚(·)isamodality-specific
2.4 PositionofThisWork
summary encoder. The summary vector s𝑚 captures the global
VGMRcomplementsbothoptimization-levelbalancingmethods stateofmodality𝑚 andisusedforsummary-levelcross-modal
andfusion-orientedinteractionmethods.Optimization-levelap- interaction.Sinceinteractionisperformedatthesummarylevel,
proachesadjustlosses,gradients,ormodalityweightsduringjoint VGMRdoesnotrequirestricttime-stepalignmentacrossmodalities.
training,whilefusionmethodsmainlyfocusonhowtoaggregate,
align,orexchangeinformationaftermodalityrepresentationshave 3.3 Cross-ModalInteractionModeling
enteredthefusionstage.Incontrast,VGMRactsbeforefusionby Toestimatethevalueofatargetmodality,VGMRconsidersnot
refiningoriginalmodalityfeatureswithcontext-conditionedvalue onlythemodalityitselfbutalsoitsrelationshipwiththeremaining
evidence. modalities.Foreachtargetmodality𝑚∈M,wedefinethesetof
Differentfromattention,confidenceestimation,reliabilityweight- non-targetmodalitiesas
ing,orgenericgating,VGMRdoesnottreatvalueasadirectpreser-
vationscoreorasstandalonemodalityreliability.Instead,ites-
N𝑚 =M\{𝑚}. (4)
timates global-level and channel-level value signals as context- Here,N𝑚containsallmodalitiesexceptthecurrenttargetmodality.
conditionedimpactevidenceundercross-modalagreementand Forexample,inatext-audio-visionsetting,when𝑚=𝑡,thenon-
discrepancy. A high value indicates that a modality or channel targetsetisN𝑡 ={𝑎,𝑣}.
maystronglyaffectthefinalpredictionunderthecurrentcontext, Wefirstaggregatethesummariesofnon-targetmodalitiesto
butitdoesnotbyitselfdeterminewhetherthecorrespondingfea- obtainacross-modalcontext:
tureshouldbepreservedorsuppressed.Thefinalgatecombines 1 ∑︁
valueevidencewithrawandprojectedfeatureevidencetolearn u𝑚 = card(N𝑚) s𝑜 . (5)
themodulationdirectionthroughend-to-endtasksupervision. 𝑜∈N𝑚
Thisdesignseparateswherecontextualimpactmayexistfrom Here,card(N𝑚)denotesthenumberofnon-targetmodalities,and
howeachfeatureshouldbemodulated.Bydoingso,VGMRprovides u𝑚 ∈ R𝑑𝑝 representstheaveragecontextualreferenceprovided
apre-fusionvalue-conditionedrefinementmechanismthatcanhelp bytheremainingmodalities.Inabimodalsetting,u𝑚 issimply
preservetask-relevantcomplementarycueswhilereducingnoisy thesummaryoftheothermodality;inatrimodalsetting,itisthe
orconflictingresponsesbeforemultimodalfusion. averagesummaryofthetwonon-targetmodalities.

JiyuanLiu,LiangweiNathanZheng,WeiEmmaZhang,XinpeiWang,andWeitongChen
Figure1:OverviewoftheproposedValue-GatedModalityRefiner(VGMR).Foreachmodality,VGMRfirstprojectsrawfeatures
intoasharedlatentspaceandbuildsasummaryrepresentation(Section3.2).Itthenconstructssummary-levelcross-modal
interactionsbymodellingagreementanddiscrepancybetweenthetargetmodalityandnon-targetmodalities(Section3.3).
Basedontheseinteractions,VGMRestimatesglobal-levelandchannel-levelvaluesignalsasimpactevidence(Section3.4),
combinesthemwithfeatureevidencetogeneratefine-grainedgates(Section3.5),andappliesgateamplificationwithresidual
retention(Section3.6).Thefinaleffectivegaterefinestheoriginalmodalityfeaturebeforemultimodalfusion(Section3.7).
Foreachnon-targetmodality𝑜 ∈ N𝑚,wecomputepairwise context,agreement,anddiscrepancy.Therefore,z𝑚shouldbeun-
agreementanddiscrepancy: derstoodascontext-conditionedimpactevidence,ratherthanasa
directuseful/uselessclassifier.
|     |      | =s𝑚 ⊙s𝑜 | ,   | =|s𝑚−s𝑜|. |     |     |     |     |     |     |     |
| --- | ---- | ------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
|     | a𝑚,𝑜 |         |     | 𝜹𝑚,𝑜      |     | (6) |     |     |     |     |     |
Basedonz𝑚,VGMRestimatesaglobalvaluesignalandachannel-
| Wedenotethecollectionsofpairwiseagreementanddiscrepancy |     |     |     |     |     |     | levelvaluesignal: |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- |
termsas
|                 |        |          |                  |           |                  |     |        | 𝑔                 | 𝑔                                  | 𝑝           | 𝑝       |
| --------------- | ------ | -------- | ---------------- | --------- | ---------------- | --- | ------ | ----------------- | ---------------------------------- | ----------- | ------- |
|                 |        |          |                  |           |                  |     |        | 𝑔 𝑚 =𝜎((w𝑚 )⊤z𝑚+𝑏 | ), p𝑚                              | =𝜎(W𝑚 z𝑚+b𝑚 | ), (10) |
| A𝑚              | ={a𝑚,𝑜 | |𝑜 ∈N𝑚}, |                  | D𝑚 ={𝜹𝑚,𝑜 | |𝑜 ∈N𝑚}.         | (7) |        |                   | 𝑚                                  |             |         |
|                 |        |          |                  |           |                  |     | where𝑔 | ∈Randp𝑚           | ∈R𝑑𝑝.Thesigmoidfunction𝜎(·)mapsthe |             |         |
| The interaction | input  | is       | then constructed |           | by concatenating | the |        | 𝑚                 |                                    |             |         |
𝑔 ∈R𝑑𝑝
targetsummary,non-targetsummaries,pairwiseagreementterms, estimatedvaluesignalsintoaboundedrange.Thevectorw𝑚
|                                                 |                     |     |             |             |              |     | andscalarbias𝑏 | 𝑔                          | Raremodality-specificparametersusedto |                      |                        |
| ----------------------------------------------- | ------------------- | --- | ----------- | ----------- | ------------ | --- | -------------- | -------------------------- | ------------------------------------- | -------------------- | ---------------------- |
| pairwisediscrepancyterms,andtheaveragedcontext: |                     |     |             |             |              |     |                | 𝑚 ∈                        |                                       |                      |                        |
|                                                 |                     |     |             |             |              |     | p ro           | d u c e t h e g lo b a l v | al u e 𝑔 𝑚 . T h is s c               | a la r c a p tu re s | s a m p l e -l e v e l |
| r𝑚 =𝜓                                           | (cid:0)[s𝑚;{s𝑜}𝑜∈N𝑚 |     | ;{a𝑚,𝑜}𝑜∈N𝑚 | ;{𝜹𝑚,𝑜}𝑜∈N𝑚 | ;u𝑚](cid:1). | (8) |                |                            |                                       |                      |                        |
𝑚 im p a c t ev i d en c e f o r th e w h ol e m o da l i ty u n d e r th e c u r re n t c r o s s -
modalcontext.
Theagreementtermsprovidefeature-wiseco-activationevidence
|     |     |     |     |     |     |     |     | 𝑝 ∈ | R𝑑𝑝×𝑑𝑝 | 𝑝 ∈ R𝑑𝑝 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------- | --- |
betweenthetargetmodalityandeachnon-targetmodality,while ThematrixW𝑚 andbiasvectorb𝑚 areused
toproducethechannel-levelvaluep𝑚.Unlike𝑔
thediscrepancytermsprovidepairwisemismatchevidence.Itcap- 𝑚,whichgivesan
turesfeature-wiseco-activationandindicateswhichlatentdimen- overallvalueestimateformodality𝑚,p𝑚providesdimension-wise
sionsaresupportedbyboththetargetmodalityandtheremaining valueevidenceinthesharedlatentspace.ThisallowsVGMRto
|                                 |     |     |     | R𝑑𝑝 |                 |     | identifywhichlatentchannelsmayrequirestrongermodulation. |     |     |     |     |
| ------------------------------- | --- | --- | --- | --- | --------------- | --- | -------------------------------------------------------- | --- | --- | --- | --- |
| modalities.Thediscrepancyterm𝜹𝑚 |     |     |     | ∈   | iscomputedbythe |     |                                                          |     |     |     |     |
absolutedifferencebetweensummaries.Itcapturescross-modal Theglobalvalueandchannel-levelvalueplaydifferentroles.
Theglobalvalue𝑔
mismatch,whichmayreflectcomplementaryinformation,modality 𝑚providescoarsemodality-levelcontext,while
conflict,orpotentialnoise.Thus,thepairwiseagreementterms thechannelvaluep𝑚providesfinerdimension-levelevidence.Both
provideconsistencyevidence,whilethepairwisediscrepancyterms are used to condition gate generation, but neither of them is a
directretentionmask.Alargervaluemeansthatthecorresponding
providemismatchevidence.
modalityorchannelhasstrongercontextualimpact,whichmay
3.4 ModalityValueEstimation leadtoenhancementorsuppressiondependingonthefinalgate
generator.
Giventhemodalitysummarys𝑚andthecross-modalinteraction
representationr𝑚,VGMRfirstlearnsahiddenvaluerepresentation:
|     |     |                |     |     |       |     | 3.5 | Fine-GrainedGateGeneration |     |     |     |
| --- | --- | -------------- | --- | --- | ----- | --- | --- | -------------------------- | --- | --- | --- |
|     | z𝑚  | =𝜂 𝑚([s𝑚;r𝑚]), |     | z𝑚  | ∈R𝑑𝑝. | (9) |     |                            |     |     |     |
Beforebeingmappedintogatelogits,theboundedvaluesignals
Here,𝜂
| 𝑚(·)isalearnablemodality-specificvalueencoder,andz𝑚 |     |     |     |     |     |     | arecentered: |     |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- |
isthelatentrepresentationusedforvalueestimation.Theinput
[s𝑚;r𝑚]combinesmodality-specificinformationwithcross-modal 𝑔 ′ =2𝑔 𝑚−1, p𝑚 ′ =2p𝑚−1.
𝑚

BeforeFusion,AskWhattoKeep:ContextualCalibrationofMultimodalSignals
|     |     |     |     |     |     |     |     | 3.7 | ModalityRefinement |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- |
=𝜎(cid:0)𝜌 𝑥(X𝑚)⊕𝜌 ℎ(H𝑚)⊕𝜌 𝑔 (𝑔 ′ )⊕𝜌 𝑝 ′ )(cid:1). Finally,theeffectivegateG¯ 𝑚 isappliedtotheoriginalmodality
|     | G𝑚  | 𝑚   |     | 𝑚   | 𝑚 𝑚 𝑚 | (p𝑚 | (11) |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | ----- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
feature:
|     | H e re , ⊕ | d e no te s | e l e m e n | t -w is e a d | d it io n a f t e r s h | a p e a li | g n m e n t. |     |     |           |         |             |     |     |
| --- | ---------- | ----------- | ----------- | ------------- | ----------------------- | ---------- | ------------ | --- | --- | --------- | ------- | ----------- | --- | --- |
|     |            |             |             |               |                         |            |              |     | X˜  | =Post𝑚(X𝑚 | ⊙G¯ 𝑚), | X˜ ∈R𝑇𝑚×𝑑𝑚. |     |     |
Eac h m a p pi n g fu n ct i o n 𝜌 ( · ) tra n sf o r m s o r b r o a d c a s ts i ts i n p u t to 𝑚 𝑚
thesameshapeastheoriginalfeature,namelyR𝑇𝑚×𝑑𝑚. Here,Post𝑚(·)isalightweightdimension-preservinglayerim-
Specifically,𝜌 𝑥(·)isadimension-preservingaffinelayerapplied plementedasLayerNormfollowedbyDropout.Therefinedfeature
𝑚
X˜
totheoriginalfeatureX𝑚.Itprovidesrawfeatureevidenceand 𝑚 keepsthesameshapeasX𝑚,whileitscomponentsaremod-
allowsthegatetodependdirectlyontheoriginalmodalityrepre- ulated using both value evidence and feature-level information
sentation.𝜌 ℎ(·) mapstheprojectedfeatureH𝑚 fromtheshared beforebeingfedintothemultimodalbackbone.
𝑚
| latentdimension𝑑 |     | 𝑝backtotheoriginalfeaturedimension𝑑 |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝑚.Itin-
|     |     |     |     |     |     |     |     | 3.8 | TrainingObjective |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- |
troduceslatent-spaceinformationlearnedduringvalueestimation
intogategeneration. Therefinedmodalityfeaturesarefedintoamultimodalbackbone
𝑔
The mapping 𝜌 (·) transforms the centered global value𝑔 ′ toproducethefinalprediction:
|     |        |                 | 𝑚                |          |                           |            | 𝑚           |     |     |          |       |     |     |     |
| --- | ------ | --------------- | ---------------- | -------- | ------------------------- | ---------- | ----------- | --- | --- | -------- | ----- | --- | --- | --- |
| i n | to a 𝑑 | -d i m e n si o | n a l v e c t or | a nd b r | o a d c a st s i t a l on | g t h e te | m p o r a l |     |     |          |       |     |     |     |
|     | 𝑚      |                 |                  |          |                           |            |             |     |     | 𝑦ˆ=𝑓({X˜ | 𝑚}𝑚∈M | ).  |     |     |
𝑇
| d im | e ns i on | 𝑚 . T h i s | p ro v i d e s | sa m pl e -l | e v e l m o d a l it y co | n t e xt | to e v e r y |     |     |     |     |     |     |     |
| ---- | --------- | ----------- | -------------- | ------------ | ------------------------- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
timestepandfeaturedimensionofthegate.Themapping𝜌 𝑝 Thewholemodelistrainedend-to-endwith:
𝑚 (·)
transformsthecenteredchannel-levelvaluep𝑚 ′ from𝑑 𝑝 to𝑑 𝑚and L=L𝑡𝑎𝑠𝑘(𝑦ˆ,𝑦)+𝜆 𝑣L𝑣𝑎𝑙𝑢𝑒+𝜆 𝑟L𝑟𝑒𝑔 .
| alsobroadcastsitalong𝑇 |     |     | 𝑚.Thisprovidesdimension-levelvalue |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Here,L𝑡𝑎𝑠𝑘isthestandardpredictionloss,whichprovidesthemain
evidenceforfine-grainedfeaturemodulation.
supervisionforboththebackboneandthegategenerator.Thevalue
|     |               | 𝜙             | 𝜓             | 𝜂                |                         |             |              |       |                 |                  |                  |             |                 |                      |
| --- | ------------- | ------------- | ------------- | ---------------- | ----------------------- | ----------- | ------------ | ----- | --------------- | ---------------- | ---------------- | ----------- | --------------- | -------------------- |
|     | T h e e n     | c o d e r s 𝑚 | , 𝑚 , a n     | d 𝑚 a r e        | i m p l e m e n t e d   | a s l i g h | t w e ig h t |       |                 | L                |                  |             |                 |                      |
|     |               |               |               |                  |                         |             | 𝑑            | s u p | e r v i s i o n | t e r m 𝑣 𝑎 𝑙𝑢 𝑒 | e n co u r a g e | s t h e e s | t i m a t e d v | a lu e s i g n a l s |
| tw  | o - l a y e r | M L P s w i   | th n o n l in | e a r a ct i v a | t i o n a n d o u t p u | t d i m e n | s i o n 𝑝 .  |       |                 |                  |                  |             |                 |                      |
𝑔 𝑝 t o r e fl e c t e m p i r i c a l m o d a li ty c o n t r i b u t io n . F o r e a c h m o d a l i t y , w e
| T h | e f u n c ti | o n s 𝜙 𝑚 , 𝜓 | 𝑚 ,𝜌 𝑥 , 𝜌 | ℎ , 𝜌 , a n | d 𝜌 a r e m o d al | it y - s p e | c i fi c b e - |     |     |     |     |     |     |     |
| --- | ------------ | ------------- | ---------- | ----------- | ------------------ | ------------ | -------------- | --- | --- | --- | --- | --- | --- | --- |
𝑚 𝑚 𝑚 𝑚 e st im a t e t h is c o n t r ib u t i o n b y t h e l o s s i n c r e a s e a f t e r r e m o v i n g it :
causedifferentmodalitiesmayhavedifferentfeaturedistributions
|     |     |     |     |     |     |     |     |     | Δ 𝑚 =ℓ(𝑓({X˜ | 𝑜}𝑜∈M\{𝑚} | ),𝑦)−ℓ(𝑓({X˜ |     | 𝑜}𝑜∈M | ),𝑦). |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --------- | ------------ | --- | ----- | ----- |
anddimensions.Thevalueencodersfollowthesamearchitecture
Wealigntheglobalvalue𝑔
acrossmodalities,whiletheirparametersaremodality-specificto 𝑚andtheaveragechannelvalueAvg(p𝑚)
accountforheterogeneousfeaturedistributions.Thus,thehidden withΔ 𝑚,sothatvaluescoresserveascontext-conditionedimpact
valuerepresentationsshareaconsistentfunctionaldefinitionwith- evidenceratherthanarbitrarygate-internalactivations.Thereg-
outforcingparametersharingacrossdifferentmodalities. ularizationtermL𝑟𝑒𝑔 stabilizesthevalue/gatedistributionsand
TheresultinggateG𝑚hasthesameshapeasX𝑚,enablingtime-
preventsvaluescoresfromcollapsingtoconstants.
step-levelandfeature-dimension-levelmodulation.Unlikeageneric Thevaluetermsdonotdirectlydecidewhetherafeatureshould
featuregate,G𝑚isconditionedonbothfeatureevidenceandcross- bepreservedorsuppressed.Instead,theyprovidecontextualim-
modalvalueevidence.Therefore,VGMRdoesnotassumethathigh pactevidence,whilethefinalgatelearnsthemodulationdirection
valuemeanspreservationorthatlowvaluemeanssuppression. throughend-to-endtasksupervision.
Instead,valuesignalsindicatewherecontextualimpactmayexist,
|                              |     |            |        |         |                |        |     | 4   | Experiments       |     |     |     |     |     |
| ---------------------------- | --- | ---------- | ------ | ------- | -------------- | ------ | --- | --- | ----------------- | --- | --- | --- | --- | --- |
| while                        | the | final gate | learns | whether | each component | should | be  |     |                   |     |     |     |     |     |
| enhanced,retained,orreduced. |     |            |        |         |                |        |     | 4.1 | ExperimentalSetup |     |     |     |     |     |
3.6 GateAmplificationandResidualRetention We evaluate VGMR on five multimodal datasets covering senti-
mentanalysis,actionrecognition,andaudio-visualrecognition.
SincethesigmoidgateG𝑚islimitedto[0,1],directlyusingitmay
MOSI[27]andMOSEI[26]aretext-audio-visualsentimentanal-
leadtoconservativemodulation.Wethereforetransformitintoan
ysisbenchmarks.MOSIcontains2,199utterance-levelvideoclips
amplificationgatecenteredaround1:
|     |     |     |     |     |     |     |     | from | 93 opinion | videos, | with sentiment | scores | ranging | from -3 |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---------- | ------- | -------------- | ------ | ------- | ------- |
to3,whileMOSEIisalarger-scalebenchmarkforutterance-level
|     |     |     | Gˆ 𝑚 =1+𝛼(2G𝑚−1), |     |     |     | (12) |     |     |     |     |     |     |     |
| --- | --- | --- | ----------------- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
multimodalsentimentprediction.Forbothdatasets,weusethe
| where𝛼 |     | ∈ [0,1]controlstheamplificationstrength.When𝛼 |     |     |     |     | =0, |     |     |     |     |     |     |     |
| ------ | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
binarypositive/negativeclassificationsetting.
thegatebecomesneutralanddoesnotchangethefeaturescale.A UCF101[11]isusedforhumanactionrecognitionandcontains
| larger𝛼allowsstrongerenhancementwhenG𝑚 |     |     |     |     | >0.5andstronger |     |     |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
101actionclasses,with9,537videosfortrainingand3,783videos
suppressionwhenG𝑚 <0.5. fortestingunderthestandardprotocol.EachUCF101videoisrep-
Toavoidover-suppression,weintroduceresidualretention:
resentedusingRGBframesandopticalflowsequences,whereRGB
G¯ =𝛽+(1−𝛽)Gˆ , capturesappearanceinformationandopticalflowcapturesmotion
|     |     |     | 𝑚   |     | 𝑚   |     | (13) |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
information.AVE[15]isanaudio-visualeventdatasetwith4,14310-
where𝛽 ∈ [0,1] controlstheretentionstrength.Alarger𝛽 pre- secondvideosacross28eventcategories.Weextractvisualframes
servesmoreoriginalinformationandreducestheriskofdiscarding andcorrespondingaudioclipsfromevent-localizedsegmentsand
weakbutusefulmodalitycues.Asmaller𝛽allowsstrongeradap-
followtheoriginalsplit.CREMA-D[1]isanaudio-visualemotion
tiverefinement.ThisdesignallowsthefinaleffectivegateG¯
|     |     |     |     |     |     |     | 𝑚 to | recognitiondatasetwith7,442clipsfromsixemotioncategories, |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
balanceadaptiverefinementandinformationpreservation. splitinto6,698trainingsamplesand744testingsamples.

JiyuanLiu,LiangweiNathanZheng,WeiEmmaZhang,XinpeiWang,andWeitongChen
Table2:PerformancecomparisonofdifferentmethodsunderconcatenationandTransformerbackbonesettingsacrossmultiple
multimodaldatasets.
Backbone Concatenation Transformer
Dataset MOSI MOSEI UCF101 AVE CREMA-D MOSI MOSEI
Method Acc F1 Acc F1 Acc F1 Acc F1 Acc F1 Acc F1 Acc F1
Baseline 0.7507 0.7507 0.8154 0.7850 0.7864 0.7811 0.6169 0.5816 0.5054 0.5030 0.7741 0.7732 0.8255 0.7810
MLA 0.7726 0.7712 0.8304 0.7893 0.7803 0.7747 0.6318 0.5892 0.5108 0.5081 0.7813 0.7801 0.8184 0.7737
D&R 0.7828 0.7820 0.8221 0.7904 0.7906 0.7834 0.5995 0.5614 0.4852 0.4678 0.8017 0.7990 0.8311 0.7848
OGM-GE 0.7930 0.7926 0.8234 0.7707 0.7906 0.7849 0.6468 0.6133 0.5148 0.5096 0.7843 0.7790 0.8264 0.7724
ARL 0.7886 0.7869 0.8225 0.7881 0.7917 0.7832 0.6567 0.6224 0.5753 0.5794 0.7843 0.7819 0.8268 0.7856
Grad-Blending 0.7857 0.7804 0.8251 0.7679 0.7930 0.7859 0.6567 0.6109 0.5175 0.5165 0.7886 0.7818 0.8337 0.7921
MMPareto 0.7843 0.7839 0.8281 0.7760 0.7909 0.7836 0.6443 0.6030 0.4973 0.4963 0.7901 0.7839 0.8279 0.7812
PMR 0.7843 0.7831 0.8229 0.7696 0.7975 0.7896 0.6418 0.5990 0.5175 0.5155 0.7901 0.7884 0.8332 0.7820
AGM 0.7828 0.7804 0.8300 0.7899 0.8020 0.7941 0.6294 0.5955 0.4960 0.4934 0.8003 0.7907 0.8302 0.7940
VGMR 0.7945 0.7911 0.8356 0.7894 0.8126 0.8059 0.6592 0.6199 0.5780 0.5782 0.8076 0.8019 0.8446 0.8029
Allmethodsfollowthesamedatasplitsandareevaluatedus- Theglobalvalue𝑔 𝑚providessample-levelmodalityimpactev-
ingAccuracyandMacro-F1.Unlessotherwisestated,wesetthe idence,whilethechannelvaluep𝑚providesdimension-levelevi-
gateamplificationcoefficient𝛼 to0.5andtheresidualretention denceforfine-grainedfeaturemodulation.Thesecondgroupstud-
coefficient𝛽to0.2acrossallexperiments.Forreproducibility,all iesthecross-modalevidenceusedforvalueestimation,including
comparedmethodsusethesamepreprocessing,backbone,opti- theagreementterma𝑚andthediscrepancyterm𝜹𝑚.Here,a𝑚cap-
mizer,batchsize,stoppingcriterion,andrandomseeds,withthe turescross-modalconsistencythroughfeature-wiseco-activation,
bestvalidationcheckpointusedfortestevaluation. while𝜹𝑚capturescross-modalmismatchorpotentialconflict.
ForAVEandCREMA-D,theResNet+Concatsettingusesfixed
Table3:ComponentablationofVGMRonMOSEI.
lightweightaudio-visualfeaturesandashallowfusionheadrather
thanalargepretrainedvideooraudiofoundationbackbone.There-
Condition Acc Macro-F1
fore, the absolute CREMA-D numbers should be interpreted as
FullVGMR 0.8446 0.8029
resultsunderthiscontrolledlow-capacityprotocol,whosepurpose
Valuesignalablation
istotestwhetherVGMRimprovesthesamebackbone,ratherthan
asstate-of-the-artCREMA-Dperformance. w/ochannel-signalp𝑚 0.8324 0.7831
w/oglobal-signal𝑔 𝑚 0.8390 0.8011
w/o𝑔 𝑚andp𝑚 0.8287 0.7917
Agreement–discrepancyablation
4.2 OverallPerformance
w/oagreementA𝑚 0.8347 0.7965
Table2reportstheoverallperformanceacrossfivedatasetsand
w/odiscrepancyD𝑚 0.8330 0.7908
twobackbonesettings.WereportAccuracyandMacro-F1forall
w/obothA𝑚andD𝑚 0.8257 0.7812
methods.
Table 3 shows that each component contributes to the final
AsshowninTable2,VGMRachievesthebestAccuracyinmost
performanceofVGMR.Removingbothglobalandchannel-level
settingsandobtainsstrongorcompetitiveMacro-F1acrosssen-
valuesignalsleadstoaclearperformancedrop,indicatingthat
timentanalysis,actionrecognition,andaudio-visualrecognition
explicitvalueevidenceisimportantforgategeneration.Usingonly
tasks.
Under the ResNet+Concat backbone, VGMR consistently im-
𝑔 𝑚giveslimitedimprovement,suggestingthatasinglesample-level
value signal is too coarse for fine-grained modality refinement.
provesovertheplainbaselineonMOSI,MOSEI,UCF101,AVE,and
CREMA-D,showingthattheproposedrefinerisnotlimitedtotext-
Using only p𝑚 performs better, especially on Macro-F1, which
showsthatchannel-levelvalueevidenceismoredirectlyusefulfor
audio-visualsentimentdatasets.UndertheTransformerbackbone,
selectivefeaturemodulation.However,thefullmodelstillachieves
VGMRachievesthebestresultsonbothMOSIandMOSEI,reaching
0.8446Accuracyand0.8029Macro-F1onMOSEI.AlthoughARL
thebestresult,indicatingthat𝑔 𝑚andp𝑚providecomplementary
conditioning:theformersuppliesoverallmodality-levelcontext,
obtainsslightlyhigherMacro-F1onAVEandCREMA-D,VGMR
whilethelattersupportsfinerchannel-levelrefinement.
achievesthebestAccuracyandremainscompetitiveinMacro-F1.
Theagreement–discrepancyablationfurthershowsthatvalue
Overall,theseresultssuggestthatVGMRcanserveasageneral
estimationbenefitsfrombothconsistencyandconflictevidence.Re-
pre-fusionrefinementmoduleacrossdifferentbackbonesandtasks.
movingeithera𝑚or𝜹𝑚weakensperformance,andremovingboth
causesthelargestdrop.Thissuggeststhatagreementhelpsidentify
modalitycomponentssupportedbyothermodalities,whilediscrep-
4.3 ComponentAblation
ancyhelpsdetectunreliableorconflictingresponses.Thelarger
WeconducttwogroupsofablationstudiesonMOSEI.Thefirst decreasecausedbyremoving𝜹𝑚indicatesthatconflictevidence
groupstudiesthevaluesignalsusedforgateconditioning,including isparticularlyimportantforweak-modalityrefinement.Overall,
theglobalvalue𝑔 𝑚andthechannel-levelvaluep𝑚. thebestperformanceisobtainedonlywhenglobalvalue,channel

BeforeFusion,AskWhattoKeep:ContextualCalibrationofMultimodalSignals
value,agreement,anddiscrepancyareusedtogether,confirming Transformerbackbone.Allcontrolledbaselinesusethesameinput
thatVGMRreliesonmulti-levelvalueevidenceratherthanasingle features,datasplit,Transformerbackbone,andtrainingprotocol.
scalarscoreoragenericfeaturegate.
|     |     |     |     |     | Table 6: Comparison | with generic | interaction | and gating |
| --- | --- | --- | --- | --- | ------------------- | ------------ | ----------- | ---------- |
4.4 Value-GuidedGateBehaviorAnalysis
mechanismsonMOSEIwiththeTransformerbackbone.
Weconductatext-corruptionanalysisonMOSIwiththeConcat
backbone.Inthecorruptedcondition,30%oftexttimestepsare Method Acc Macro-F1
replacedwithGaussiannoise.Wefocusonthetextmodalityand
|     |     |     |     |     |     | Concat | 0.8255 0.7810 |     |
| --- | --- | --- | --- | --- | --- | ------ | ------------- | --- |
reportfourstatistics:globalvalue,channelvalue,channel-value
|     |     |     |     |     |     | Cross-Attention | 0.8317 0.7941 |     |
| --- | --- | --- | --- | --- | --- | --------------- | ------------- | --- |
standarddeviation,andaverageinitialgateresponse.Theglobal Sigmoid+TanhGate 0.8326 0.7924
valuereflectssample-levelcontextualimpact,whilethechannel
|     |     |     |     |     |     | VGMR | 0.8446 0.8029 |     |
| --- | --- | --- | --- | --- | --- | ---- | ------------- | --- |
valuereflectsdimension-levelimpactevidence.Thechannel-value
standarddeviationmeasureshowunevenlythevalueevidenceis
distributedacrosschannels.Thegateresponseindicatestheaverage
initialmodulationstrengthassignedtothecorruptedorcleantext Table 7: Efficiency comparison on MOSEI with the Trans-
| features. |     |     |     |     | formerbackbone. |     |     |     |
| --------- | --- | --- | --- | --- | --------------- | --- | --- | --- |
ForGlobalValue,ChannelValue,andGate,resultsarereportedas
mean±samplestandarddeviationacrosstestsamples.ForChannel Method Params ExtraParams Train/Epoch Infer./Batch
Std,wefirstcomputethestandarddeviationacrosschannelswithin Concat 0.72M 0.00M 4.26s 1.17ms
eachsample,andthenreportitsmeanandstandarddeviationacross Grad-Blending 0.77M 0.05M 13.24s 1.20ms
|             |     |     |     |     | AGM        | 0.77M | 0.05M 17.71s | 1.18ms |
| ----------- | --- | --- | --- | --- | ---------- | ----- | ------------ | ------ |
| thetestset. |     |     |     |     | Concat+MLP | 3.04M | 2.32M 4.82s  | 1.33ms |
Table4:Valueandgateresponseundertextcorruptionon Cross-Attention 3.06M 2.33M 7.32s 2.86ms
|     |     |     |     |     | Sigmoid+TanhGate | 3.07M | 2.35M 5.25s | 1.46ms |
| --- | --- | --- | --- | --- | ---------------- | ----- | ----------- | ------ |
MOSI.
|           |             |              |            |      | VGMR | 3.04M | 2.32M 10.01s | 3.87ms |
| --------- | ----------- | ------------ | ---------- | ---- | ---- | ----- | ------------ | ------ |
| Condition | GlobalValue | ChannelValue | ChannelStd | Gate |      |       |              |        |
ForConcat+MLPandSigmoid+TanhGate,weadjustthehidden-
| CleanText | 0.598±0.119 | 0.554±0.092 | 0.102±0.120 | 0.481±0.039 |     |     |     |     |
| --------- | ----------- | ----------- | ----------- | ----------- | --- | --- | --- | --- |
dimensionalsettingstomaketheirparametercountsclosetoVGMR.
| NoisyText | 0.788±0.062 | 0.707±0.030 | 0.301±0.053 | 0.417±0.009 |                                                  |     |     |     |
| --------- | ----------- | ----------- | ----------- | ----------- | ------------------------------------------------ | --- | --- | --- |
| Δ         |             |             |             |             | AsshowninTables5and6,VGMRoutperformsearly-fusion |     |     |     |
|           | +0.190      | +0.153      | +0.199      | -0.064      |                                                  |     |     |     |
strategies,Cross-Attention,andgenericlearnablegating.Compared
AsshowninTable4,textcorruptionincreasestheglobalvalue,
withthebestearly-fusionbaselinesoneachmetric,VGMRimproves
channelvalue,andchannel-valuestandarddeviation,butdecreases
AccuracyandMacro-F1by1.48and1.58percentagepoints,respec-
theaveragegateresponse.Thispatternsuggeststhatthecorrupted
tively.ItalsoimprovesoverCross-AttentionandSigmoid+Tanh
textproducesstrongercontextualimpactandmoreunevenchannel- Gateunderthesamebackbonesetting.Theseresultssuggestthat
levelevidence,indicatingthatthemodeldetectsitasahigh-impact
|                 |             |          |           |               | the gain cannot | be fully attributed | to stronger feature | aggrega- |
| --------------- | ----------- | -------- | --------- | ------------- | --------------- | ------------------- | ------------------- | -------- |
| input requiring | modulation. | However, | the lower | gate response |                 |                     |                     |          |
tion,genericcross-modalrelevancemodelling,orsimplyalarger
showsthathighervaluedoesnotdirectlymeanstrongerpreser-
learnablemodule.Instead,theyindicatethatusingcross-modal
| vation. Instead, | value | signals provide | impact evidence, | and the |     |     |     |     |
| ---------------- | ----- | --------------- | ---------------- | ------- | --- | --- | --- | --- |
agreementanddiscrepancyasvalueevidenceforgategeneration
gategeneratorcombinesthisevidencewithfeatureinformationto providesadditionalbenefitsbeforemultimodalfusion.
suppressunreliablehigh-impactresponsesbeforefusion.
Table7reportstotalparameters,extraparameters,trainingtime
perepoch,andinferencelatencyperbatch.VGMRincreasesthe
4.5 ControlledComparisonandEfficiency
parametercountfrom0.72Mto3.04Mandinferencelatencyfrom
Analysis
1.17msto3.87msperbatchcomparedwiththevanillaTransformer.
Therefore,VGMRintroducesanacceptablebutnon-negligiblecom-
Table 5: Fusion strategy comparison on MOSEI with the putationaloverheadoverthesimplestbackbone.
Transformerbackbone. However,theperformancegainisunlikelytobeexplainedsolely
bytheincreasedparametercount.Afteradjustingthehiddendi-
mensions,Concat+MLPhasalmostthesamenumberofparameters
|     | Method | Acc | Macro-F1 |     |     |     |     |     |
| --- | ------ | --- | -------- | --- | --- | --- | --- | --- |
asVGMR,whileSigmoid+TanhGatehasaslightlylargerparameter
|     | Summation | 0.8219 | 0.7785 |     |     |     |     |     |
| --- | --------- | ------ | ------ | --- | --- | --- | --- | --- |
countthanVGMR.Nevertheless,VGMRachieveshigherAccuracy
|     | TensorFusion | 0.8289 | 0.7871 |     |     |     |     |     |
| --- | ------------ | ------ | ------ | --- | --- | --- | --- | --- |
andMacro-F1thantheseparameter-comparablealternativesinTa-
|     | Concat+MLP | 0.8298 | 0.7803 |     |     |     |     |     |
| --- | ---------- | ------ | ------ | --- | --- | --- | --- | --- |
bles5and6.ThissuggeststhattheadvantageofVGMRcomesnot
|     | VGMR | 0.8446 | 0.8029 |     |     |     |     |     |
| --- | ---- | ------ | ------ | --- | --- | --- | --- | --- |
onlyfromaddingmoreparameters,butfromhowtheseparame-
tersareusedtoestimatemodalityvalueandrefinefeaturesbefore
| To examine | whether | the improvement | of VGMR | mainly comes | fusion. |     |     |     |
| ---------- | ------- | --------------- | ------- | ------------ | ------- | --- | --- | --- |
from stronger feature aggregation, generic gating, or simply a Intermsofcomputationalcost,VGMRismoreexpensivethan
largerparameterbudget,wecompareitwithearly-fusionstrategies lightweightpre-fusionalternatives,especiallyininferencelatency.
andpre-fusioninteraction/gatingmechanismsonMOSEIwiththe However,itstrainingtimeremainslowerthanoptimization-level

JiyuanLiu,LiangweiNathanZheng,WeiEmmaZhang,XinpeiWang,andWeitongChen
balancingmethodssuchasGrad-BlendingandAGM,anditsabso- 4.8 MultimodalNoiseRobustnessAnalysis
luteinferencelatencyisstillwithinasmallmillisecondrangein
thissetting.Overall,VGMRprovidesareasonablebutnotcost-free
0.80
| performance–robustness                     |     |     | trade-off | when | parameter-comparable |     |      |     |     |     |
| ------------------------------------------ | --- | --- | --------- | ---- | -------------------- | --- | ---- | --- | --- | --- |
| gainsandstrongernoiserobustnessaredesired. |     |     |           |      |                      |     | 0.75 |     |     |     |
0.70
4.6 CompatibilitywithOptimization-Level
0.65
| Balancing |     |     |     |     |     |     | ccA |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.60
Table8:Plug-inanalysisofVGMRonMOSEIwiththeTrans-
| formerbackbone. |     |     |     |     |     |     | 0.55 |     |     |     |
| --------------- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- |
Grad-Blending Transformer
0.50
Pure Transformer
| Method |     | VGAcc |     | VGF1 | PlainAcc | F1  |     | VGMR Transformer |     |     |
| ------ | --- | ----- | --- | ---- | -------- | --- | --- | ---------------- | --- | --- |
0.45
| OGM-GE | 0.8367(+0.0103) |     | 0.7914(+0.0190) |     | 0.8264 | 0.7724 |     |             |             |             |
| ------ | --------------- | --- | --------------- | --- | ------ | ------ | --- | ----------- | ----------- | ----------- |
|        |                 |     |                 |     |        |        |     | 0.1 0.2 0.3 | 0.4 0.5 0.6 | 0.7 0.8 0.9 |
| ARL    | 0.8343(+0.0075) |     | 0.7870(+0.0014) |     | 0.8268 | 0.7856 |     |             |             |             |
Noise Ratio
WeapplyVGMRtoOGM-GEandARLundertheMOSEITrans-
formersetting.AsshowninTable8,addingVGMRconsistently Figure2:NoiserobustnessonMOSIunderdifferentnoise
| improvesbothmethods.OGM-GEgains1.01percentagepointsin |     |     |     |     |     |     | ratios. |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- |
Accuracyand1.90percentagepointsinF1,whileARLgains0.75
and0.14percentagepoints,respectively.Theseresultssuggestthat
VGMRcanworktogetherwithtraining-stagebalancingmethods,
sinceitrefinesmodalityfeaturesbeforefusionratherthanonly
0.75
adjustingoptimizationafterfusion.
0.70
4.7 Weak-ModalityInterferenceAnalysis
ccA
0.65
Table9:ModalityremovalanalysisonMOSEIwiththeTrans-
formerbackbone.
0.60
Grad-Blending Transformer
| Method | FullAcc |     | w/oText | w/oAudio |     | w/oVision | 0.55 |     |     |     |
| ------ | ------- | --- | ------- | -------- | --- | --------- | ---- | --- | --- | --- |
Pure Transformer
Concat 0.8255 0.7053(-0.1202) 0.8092(-0.0163) 0.8253(-0.0002) VGMR Transformer
| Grad-Blending | 0.8337 | 0.7096(-0.1241) |     | 0.8317(-0.0020) | 0.8343(+0.0006) |     |     |     |     |     |
| ------------- | ------ | --------------- | --- | --------------- | --------------- | --- | --- | --- | --- | --- |
OGM-GE 0.8264 0.7094(-0.1170) 0.8255(-0.0009) 0.8244(-0.0020) 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0
PMR 0.8332 0.7102(-0.1230) 0.8324(-0.0008) 0.8332(+0.0000) Noise Weight
| ARL      | 0.8268 | 0.7102(-0.1166) |     | 0.8246(-0.0022) | 0.8270(+0.0002) |     |     |     |     |     |
| -------- | ------ | --------------- | --- | --------------- | --------------- | --- | --- | --- | --- | --- |
| MMPareto | 0.8279 | 0.7102(-0.1177) |     | 0.8289(+0.0010) | 0.8291(+0.0012) |     |     |     |     |     |
Figure3:NoiseintensityrobustnessonMOSIunderdifferent
| D&R | 0.8311 | 0.7092(-0.1219) |     | 0.8302(-0.0009) | 0.8330(+0.0019) |     |     |     |     |     |
| --- | ------ | --------------- | --- | --------------- | --------------- | --- | --- | --- | --- | --- |
noiseweights.
| MLA  | 0.8184 | 0.7062(-0.1122) |     | 0.8161(-0.0023) | 0.8184(+0.0000) |     |     |     |     |     |
| ---- | ------ | --------------- | --- | --------------- | --------------- | --- | --- | --- | --- | --- |
| AGM  | 0.8302 | 0.7105(-0.1197) |     | 0.8283(-0.0019) | 0.8296(-0.0006) |     |     |     |     |     |
| VGMR | 0.8446 | 0.7102(-0.1344) |     | 0.8410(-0.0036) | 0.8371(-0.0075) |     |     |     |     |     |
Toexaminerobustnesstocorruptedmodalityinputs,weconduct
WeconductmodalityremovalanalysisonMOSEItoexamine noiseexperimentsonMOSIbyinjectingGaussiannoiseintoall
weak-modalityinterference.Here,w/oText,w/oAudio,andw/o rawalignedmodalityfeaturesbeforetheyenterthemodel.Masked
Visiondenoteremovingonemodalityandusingtheremainingtwo. entriesarereplacedwithnoisesampledusingtheper-featuremean
AsshowninTable9,removingtextcausesalargeperformance andstandarddeviationcomputedfromthetrainingsplit.Weeval-
dropforallmethods,confirmingthattextisthedominantmodality. uatetwosettings:varyingthenoiseratiowithfixedgranularity,
However,severalbalancingmethodsachievehigheraccuracyafter andvaryingthenoiseweightwithfixedratio.Eachsettingisrun
removingaudioorvision,indicatingthataudioandvisualmodali- withthreerandomseeds,andwereporttheaverageaccuracywith
| tiescanintroducenoisyorlow-valuecomponentswhendirectly |     |     |     |     |     |     | variationbands. |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- |
usedinjointoptimization. AsshowninFigures2and3,allmethodsdegradeasthenoise
Incontrast,VGMR’sperformancedecreaseswheneitheraudio ratioornoiseweightincreases,butVGMRconsistentlymaintains
orvisionisremoved.ThissuggeststhatVGMRdoesnotsimply higheraccuracythanthePureTransformerandGrad-Blending
increasetheweightofweakmodalities.Instead,itusescontext- Transformer.Theadvantagebecomesmorevisibleunderheavier
conditionedvaluesignalstoguidegategeneration,allowingthe corruption,suggestingthatpre-fusionvaluerefinementhelpswhen
modeltolearnwhichweak-modalityresponsesshouldberetained multimodalinputscontainnoisycomponents.ComparedwithGrad-
orreducedbeforefusion.Overall,theresultsareconsistentwithour Blending,whichbalancesmodalitylearningduringoptimization,
motivationthatthekeychallengeisnotwhetherweakmodalities VGMRcanreducetheinfluenceofcorruptedfeaturesbeforefu-
shouldbeused,buthowtoidentifyandretaintheirtask-relevant sion,leadingtomorestableperformanceundernoisymultimodal
| partswhensuchpartsareuseful. |     |     |     |     |     |     | conditions. |     |     |     |
| ---------------------------- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- |

BeforeFusion,AskWhattoKeep:ContextualCalibrationofMultimodalSignals
4.9 OptimizationStabilityAnalysis
0.4
| WefirstcomparethetrainingandvalidationlosscurvesonMOSEI. |     |     |     | tilps dilav no enisoc tneidarG |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | ------------------------------ | --- | --- | --- |
AsshowninFigure4,VGMRdecreasesquicklyatthebeginningof
0.2
trainingandmaintainsasmoothervalidationtrendinlaterepochs.
| ThissuggeststhatVGMRcanprovidecleanerinputstotheback- |     |     |     | 0.0 |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
boneandisassociatedwithmorestablemultimodaloptimization.
−0.2
1.2
|     | VGMR Train | Grad-Blending Train | PMR Train |     |     |     |     |
| --- | ---------- | ------------------- | --------- | --- | --- | --- | --- |
−0.4
| 1.1 | VGMR Val | Grad-Blending Val | PMR Val |     |     |     |     |
| --- | -------- | ----------------- | ------- | --- | --- | --- | --- |
Transformer smoothed (window=2)
| 1.0      |     |     |     | −0.6 |      | VGMR smoothed (window=2) |       |
| -------- | --- | --- | --- | ---- | ---- | ------------------------ | ----- |
|          |     |     |     |      | 5 10 | 15 20                    | 25 30 |
| ssoL 0.9 |     |     |     |      |      | Epoch                    |       |
0.8
Figure5:GradientconflictanalysisonMOSEI.
0.7
0.6
0.5
5 10 15 20 25 gate refinement can reduce unstable cross-modal coupling and
Epoch encouragemorebalancedcomplementaryoptimizationbeforemul-
timodalfeaturesenterthesharedbackbone.
Figure4:TrainingandvalidationlosscurvesonMOSEI.
4.10 QualitativeCaseStudy
Wefurtherexaminethegradient-directionrelationshipbetween
audio-onlyandaudio-videolearning,inspiredbyrecentgradient-
| basedanalysesofmodalityconflict[4].Foreachcheckpoint,we |     |     |     |     |     |     | 4   |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Text
computeanaudio-onlygradient𝑔
|     |     | audio andanaudio-videogradient |     |     |     |     | 2 egnahC |
| --- | --- | ------------------------------ | --- | --- | --- | --- | -------- |
𝑔
audio+video onthevalidationsplit.Tomakethemcomparable,both
|     |     |     |     | Audio |     |     | 0   |
| --- | --- | --- | --- | ----- | --- | --- | --- |
gradientsarecomputedwithrespecttothesamesharedparameters,
| includingthesharedTransformerbackboneandfinalprediction     |     |     |     |        |     |     | 2   |
| ----------------------------------------------------------- | --- | --- | --- | ------ | --- | --- | --- |
| head,whilemodality-specificinputprojectionlayersandinactive |     |     |     | Vision |     |     |     |
4
branchesareexcluded.Thegradientsareflattenedandconcatenated 0 9 19 29 39 49
| beforecomputing: |     |     |     |     | Timestep |     |     |
| ---------------- | --- | --- | --- | --- | -------- | --- | --- |
𝑔⊤ 𝑔
audio+video
|     | cos(𝑔 ,𝑔          | )= audio            | . (14) |       | 0.128 |     |       |
| --- | ----------------- | ------------------- | ------ | ----- | ----- | --- | ----- |
|     | audio audio+video | ∥𝑔 ∥ ∥𝑔             | ∥      | Text  |       |     |       |
|     |                   | audio 2 audio+video | 2      |       |       |     |       |
|     |                   |                     |        | Audio |       |     | 3.281 |
Thismetricisusedasadiagnosticsignalforcross-modaloptimiza-
tioncoupling.Alargepositivevalueindicatesthattheaudio-video Vision 2.340
gradientishighlyalignedwiththeaudio-onlygradient,suggest- 0 1 2 3 4
ingstrongcouplingorpotentialdominanceofaudio-relatedopti- Mean max(0, Raw - Refined)
mizationdirections.Anegativevalueindicatesdirectionalconflict,
Figure6:Sample-levelvisualizationofVGMRfeaturerefine-
wherethejointaudio-videoupdatemovesagainsttheaudio-only
mentonaMOSEItestcase.Negativechangesindicatesup-
optimizationdirection.FollowingUniX-stylegradientdiagnostics,
pressedfeatureresponses.
asmoothercurvearoundzeroispreferred,asitsuggestsweaker
cross-modaldominanceandlessseveredirectionalconflict,while
TofurtherunderstandhowVGMRrefinesmodalityfeatures,we
allowingrelativelyindependentmodalitycontributions.
AsshowninFigure5,theplainTransformershowslargerfluctu- presentaqualitativecasestudyonaMOSEItestsamplewhere
ationsbetweenpositiveandnegativecosinevalues.Thissuggests thebaselinemodelgivesanincorrectprediction,whileVGMRpro-
unstablecross-modalcoupling:thejointaudio-videooptimization ducesamoreaccurateresult.Theground-truthlabelis-2.3333.The
directionsometimesbecomesstronglyalignedwiththeaudio-only baselinepredicts0.1091,whereasVGMRpredicts-2.0747,whichis
closertothegroundtruth.
| direction,butatothertimesmovesagainstit. |     | Suchoscillations |     |     |     |     |     |
| ---------------------------------------- | --- | ---------------- | --- | --- | --- | --- | --- |
indicatethataddingvisualinformationmayintroduceunstable AsshowninFigure6,theheatmapvisualizestherefinement
differenceΔX=X˜
dominanceorinterferenceinthesharedoptimizationspace. −X,wherenegativevaluesindicatesuppressed
Incontrast,VGMRproducesasmoothercurveclosertozero. featureresponses.Thebarplotreportstheaveragesuppressionmag-
FollowingtheUniX-styleinterpretation,thisdoesnotmeanthat nitude,computedfromthepositivepartofX−X˜.Forthissample,
theaudio modality isignored. Rather, itsuggeststhatthe joint VGMRsuppressesaudioandvisualresponsesmorestrongly,while
audio-videoupdateislessdominatedbyasinglemodality-specific thetextmodalityisonlyslightlychanged.Thiscaseisconsistent
directionandavoidsstrongnegativeconflict.Thisprovidesdiagnos- withtheviewthatVGMRperformsinstance-levelandmodality-
ticevidenceconsistentwithourmotivationthatvalue-conditioned awarerefinementratherthanapplyingafixedmodality-levelweight.

JiyuanLiu,LiangweiNathanZheng,WeiEmmaZhang,XinpeiWang,andWeitongChen
Text 2
Audio 0
Vision 2
0 9 19 29 39 49
Timestep
Text 0.091
Audio 2.965
Vision 1.448
0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5
Mean max(0, Raw - Refined)
egnahC
5 FutureWork
AlthoughVGMRachievesstrongorcompetitiveperformanceacross
multipledatasets,severaldirectionsremainforfuturework.
First,VGMRshouldbefurtherevaluatedintermsofscalability
andefficiency.AsshowninTable7,itintroducesacceptablebut
non-negligibleoverhead,especiallyininferencelatency.Future
workcouldtestlargerbackbones,longersequences,andhigher-
dimensionalfeatures,whileexploringparametersharing,low-rank
projections,orsparsegating.
Second,valueestimationcanbeextendedfromsummary-level
modellingtofinertemporalorspatialmodelling.Thecurrentpooled-
summarydesignissimpleandavoidsstrictalignment,butitmay
misslocalizedconflictssuchasocclusions,framedrops,orshort
audio-textmismatches.Window-levelortime-resolvedvalueesti-
mationmayprovidemoredetailedevidenceforgategeneration.
Third,therelationshipbetweenVGMRandmultimodalinfor-
Figure7:GlobalvisualizationofaverageVGMRfeaturere-
mationdecompositiondeservesfurtherstudy.AlthoughVGMR
finementonMOSEI.VGMRshowsstrongersuppressionin
ismotivatedbyredundancy,uniqueness,andcomplementarity,it
audioandvisualmodalitiesthanintext.
doesnotexplicitlyestimatetheseinformation-theoreticquantities.
Futureworkmayintroducediagnosticmeasuresorauxiliaryobjec-
tivestobetterconnectvalueestimationwithredundancyreduction
Figure7furthershowstheaveragerefinementpatternonMOSEI. andcomplementaryinformationpreservation.
Theglobaltrendisconsistentwiththesample-levelobservation: Finally,robustnessandinterpretabilityanalysisshouldbeex-
VGMR tends to apply stronger suppression to audio and visual panded.BeyondGaussianfeaturecorruptionandcontrolledtext
modalitieswhilekeepingtextrelativelystable. corruption,VGMRshouldbetestedundermissingmodalities,tem-
poralmasking,occlusion,sensordropouts,modalityasynchrony,
4.11 SummaryofAblationandDiagnostic anddistributionshifts.Amoresystematicanalysisofglobalval-
ues,channelvalues,gatemagnitudes,andsuppressionstrength
Analyses
acrossmodalities,classes,andnoiseconditionswouldalsohelp
Overall,theablationanddiagnosticresultssupportthemainde- characterizethelearnedbehaviour.
signchoicesofVGMR.Thecomponentablationshowsthatboth
global-levelandchannel-levelvaluesignalscontributetogategen- 6 Conclusion
eration.Theglobalvalueprovidessample-levelcontextualevidence,
Inthispaper,werevisitedmultimodalimbalancefromapre-fusion
whilethechannelvalueprovidesfinerfeature-levelevidencefor
valueestimationperspective.Insteadoftreatingweakmodalities
selectiverefinement.Theagreement–discrepancyablationfurther
asentirelyusefuloruseless,wearguedthattheymaycontainboth
showsthatvalueestimationbenefitsfrombothcross-modalconsis-
complementaryinformationandharmfulresponses.Basedonthis
tencyandconflictevidence,withdiscrepancyplayingaparticularly
motivation,weproposedValue-GatedModalityRefiner(VGMR),
important role in identifying unreliable or conflicting modality
whichestimatesglobal-levelandchannel-levelvalueevidenceun-
responses.
dercross-modalcontextandusesittoguidefine-grainedfeature
Thecorruptionandmodality-removalanalysesfurtherclarify
refinementbeforefusion.
theroleoftheproposedvaluesignal.Undertextcorruption,the
ExtensiveexperimentsandanalysesshowthatVGMRimproves
estimatedvaluescoresincreasewhiletheaveragegateresponse
multimodallearningbeyondsimplefeatureaggregation,generic
decreases,suggestingthatVGMRdoesnottreatvalueasadirect
gating,ortraining-stagerebalancing.Theresultsfurthersuggest
preservationprobability.Instead,valuerepresentscontextualim-
thatvalue-conditionedrefinementcanreduceunreliablemodality
pactforgateconditioning,andthegategeneratorcombinesthisev-
responsesbeforefusion,enhancerobustnessundernoisymulti-
idencewithfeatureinformationtosuppressunreliablehigh-impact
modalinputs,andsupportmorestableoptimizationbehaviour.
responses.Themodality-removalresultsalsoshowthatVGMRdoes
Overall,VGMRprovidesapre-fusionrefinementmechanismfor
notsimplypreserveoramplifyweakmodalities,butselectively
mitigatingmultimodalimbalance.Futureworkwillexamineits
retainstask-relevantweak-modalityinformationwhilereducing
scalabilitytolargermultimodalbackbonesandextendtheanalysis
noisyorconflictingresponses.
tobroaderincomplete-modality,retrieval,recommendation,and
Finally,thecontrolledcomparisons,plug-inanalysis,robustness
real-worldmultimodalscenarios.
tests,gradientdiagnostics,andqualitativevisualizationsindicate
thatVGMRisnotmerelyanearly-fusiontransformation,ageneric
7 GenAIUsageDisclosure
gating module, or a larger parameterized model. Its advantage
comesfromusingmulti-levelvalueevidencebeforefusion,which LargeLanguageModels(LLMs)wereusedonlyaswritingsupport
cancomplementoptimization-levelbalancingmethodsandimprove duringthepreparationofthismanuscript.Theirusewaslimited
robustnessundernoisymultimodalconditions. toimprovinggrammar,wording,clarity,andoverallreadability.

BeforeFusion,AskWhattoKeep:ContextualCalibrationofMultimodalSignals
Theydidnotcontributetotheconceptualdevelopmentofthework, [20] ShicaiWei,ChunboLuo,andYangLuo.2025.ImprovingMultimodalLearning
the design of the proposed method, the experimental setup, or viaImbalancedLearning.CoRRabs/2507.10203(2025).
[21] YakeWeiandDiHu.2024. MMPareto:BoostingMultimodalLearningwith
theinterpretation ofresults. Allresearch ideas,methodological
InnocentUnimodalAssistance.InProceedingsofthe41stInternationalConference
decisions,analyses,andreportedfindingsaretheauthors’own onMachineLearning(ProceedingsofMachineLearningResearch,Vol.235).PMLR,
originalwork. 52559–52572.
[22] YakeWei,SiweiLi,RuoxuanFeng,andDiHu.2024.DiagnosingandRe-learning
forBalancedMultimodalLearning.InProceedingsoftheEuropeanConferenceon
ComputerVision.SpringerNatureSwitzerland,71–86.
References [23] PaulL.WilliamsandRandallD.Beer.2010. NonnegativeDecompositionof
MultivariateInformation.CoRRabs/1004.2515(2010).
[1] HouweiCao,DavidG.Cooper,MichaelK.Keutmann,RubenC.Gur,AniNenkova, [24] WenmengYu,HuaXu,ZiqiYuan,andJieleWu.2021.LearningModality-Specific
andRaginiVerma.2014. CREMA-D:Crowd-SourcedEmotionalMultimodal RepresentationswithSelf-SupervisedMulti-TaskLearningforMultimodalSenti-
ActorsDataset.IEEETransactionsonAffectiveComputing5,4(2014),377–390. mentAnalysis.InProceedingsoftheAAAIConferenceonArtificialIntelligence,
doi:10.1109/TAFFC.2014.2336244 Vol.35.10790–10797.
[2] YunfengFan,WenchaoXu,HaozhaoWang,JunxiaoWang,andSongGuo.2023. [25] AmirZadeh,MinghaiChen,SoujanyaPoria,ErikCambria,andLouis-Philippe
PMR:PrototypicalModalRebalanceforMultimodalLearning.InProceedings Morency.2017.TensorFusionNetworkforMultimodalSentimentAnalysis.In
oftheIEEE/CVFConferenceonComputerVisionandPatternRecognition.20029– Proceedingsofthe2017ConferenceonEmpiricalMethodsinNaturalLanguage
20038. Processing.1103–1114.
[3] WeiHan,HuiChen,andSoujanyaPoria.2021.ImprovingMultimodalFusion [26] AmirZadeh,PaulPuLiang,SoujanyaPoria,ErikCambria,andLouis-Philippe
withHierarchicalMutualInformationMaximizationforMultimodalSentiment Morency.2018.MultimodalLanguageAnalysisintheWild:CMU-MOSEIDataset
Analysis.InProceedingsofthe2021ConferenceonEmpiricalMethodsinNatural andInterpretableDynamicFusionGraph.InProceedingsofthe56thAnnual
LanguageProcessing.9180–9192. MeetingoftheAssociationforComputationalLinguistics.2236–2246.
[4] JitaiHao,HaoLiu,XinyanXiao,QiangHuang,andJunYu.2025.Uni-X:Mit- [27] AmirZadeh,RowanZellers,EliPincus,andLouis-PhilippeMorency.2016.MOSI:
igatingModalityConflictwithaTwo-End-SeparatedArchitectureforUnified MultimodalCorpusofSentimentIntensityandSubjectivityAnalysisinOnline
MultimodalModels.CoRRabs/2509.24365(2025). OpinionVideos.CoRRabs/1606.06259(2016).arXiv:1606.06259
[5] DevamanyuHazarika,RogerZimmermann,andSoujanyaPoria.2020.MISA: [28] ZianZhai,FanLi,XingyuTan,XiaoyangWang,andWenjieZhang.2025.Graph
Modality-Invariantand-SpecificRepresentationsforMultimodalSentiment isaNaturalRegularization:RevisitingVectorQuantizationforGraphRepresen-
Analysis.InProceedingsofthe28thACMInternationalConferenceonMultimedia. tationLearning.CoRRabs/2508.06588(2025).
1122–1131. [29] DuoyiZhang,RichiNayak,andMd.AbulBashar.2024.Pre-gatingandContextual
[6] JieHu,LiShen,andGangSun.2018. Squeeze-and-ExcitationNetworks.In AttentionGate:ANewFusionMethodforMulti-modalDataTasks. Neural
ProceedingsoftheIEEEConferenceonComputerVisionandPatternRecognition. Networks179(2024),106553.
7132–7141. [30] XiaohuiZhang,JaehongYoon,MohitBansal,andHuaxiuYao.2024.Multimodal
[7] HongLi,XingyuLi,PengboHu,YinuoLei,ChunxiaoLi,andYiZhou.2023. RepresentationLearningbyAlternatingUnimodalAdaptation.InProceedings
BoostingMulti-ModalModelPerformancewithAdaptiveGradientModulation. oftheIEEE/CVFConferenceonComputerVisionandPatternRecognition.27446–
InProceedingsoftheIEEE/CVFInternationalConferenceonComputerVision. 27456.
22157–22167. [31] LiangweiNathanZheng,WeiEmmaZhang,MingyuGuo,MiaoXu,OlafMaennel,
[8] JohnEdisonArevaloOvalle,ThamarSolorio,ManuelMontesyGómez,and andWeitongChen.2025.RethinkingGatingMechanisminSparseMoE:Handling
FabioA.González.2017.GatedMultimodalUnitsforInformationFusion.InPro- ArbitraryModalityInputswithConfidence-GuidedGate.CoRRabs/2505.19525
ceedingsofthe5thInternationalConferenceonLearningRepresentations,Workshop (2025).
Track. [32] HeqingZou,MengShen,ChenChen,YuchenHu,DeepuRajan,andEngSiong
[9] XiaokangPeng,YakeWei,AndongDeng,DongWang,andDiHu.2022.Balanced Chng.2023.UniS-MMC:MultimodalClassificationviaUnimodality-Supervised
MultimodalLearningviaOn-the-flyGradientModulation.InProceedingsofthe MultimodalContrastiveLearning.InFindingsoftheAssociationforComputational
IEEE/CVFConferenceonComputerVisionandPatternRecognition.8228–8237. Linguistics:ACL2023.659–672.
[10] WasifurRahman,Md.KamrulHasan,SangwuLee,AmirAliBagherZadeh,
ChengfengMao,Louis-PhilippeMorency,andMohammedE.Hoque.2020.Inte-
gratingMultimodalInformationinLargePretrainedTransformers.InProceedings
ofthe58thAnnualMeetingoftheAssociationforComputationalLinguistics.2359–
2369.
[11] KhurramSoomro,AmirRoshanZamir,andMubarakShah.2012. UCF101:
ADatasetof101HumanActionsClassesFromVideosintheWild. CoRR
abs/1212.0402(2012).arXiv:1212.0402
[12] YiboSun,WeitongChen,andZheSun.2025.Multi-modalLearningMethodsin
MedicalImagingArea:ASurvey.DigitalSignalProcessing167(2025),105441.
[13] XingyuTan,XiaoyangWang,QingLiu,XiweiXu,XinYuan,LimingZhu,and
WenjieZhang.2026. MemoTime:Memory-AugmentedTemporalKnowledge
GraphEnhancedLargeLanguageModelReasoning.InProceedingsoftheACM
WebConference2026.4220–4231.
[14] XingyuTan,XiaoyangWang,QingLiu,XiweiXu,XinYuan,LimingZhu,and
WenjieZhang.2026. PrivGemo:Privacy-PreservingDual-TowerGraphRe-
trievalforEmpoweringLLMReasoningwithMemoryAugmentation. CoRR
abs/2601.08739(2026).
[15] YapengTian,JingShi,BochenLi,ZhiyaoDuan,andChenliangXu.2018.Audio-
VisualEventLocalizationinUnconstrainedVideos.InProceedingsoftheEuropean
ConferenceonComputerVision.252–268.
[16] Yao-HungHubertTsai,ShaojieBai,PaulPuLiang,J.ZicoKolter,Louis-Philippe
Morency,andRuslanSalakhutdinov.2019. MultimodalTransformerforUn-
alignedMultimodalLanguageSequences.InProceedingsofthe57thAnnual
MeetingoftheAssociationforComputationalLinguistics.6558–6569.
[17] AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones,
AidanN.Gomez,LukaszKaiser,andIlliaPolosukhin.2017. AttentionisAll
youNeed.InAdvancesinNeuralInformationProcessingSystems30.5998–6008.
[18] DiWang,XutongGuo,YuminTian,JinhuiLiu,LihuoHe,andXuemeiLuo.
2023.TETFN:ATextEnhancedTransformerFusionNetworkforMultimodal
SentimentAnalysis.PatternRecognition136(2023),109259.
[19] WeiyaoWang,DuTran,andMattFeiszli.2020. WhatMakesTrainingMulti-
ModalClassificationNetworksHard?.InProceedingsoftheIEEE/CVFConference
onComputerVisionandPatternRecognition.12692–12702.