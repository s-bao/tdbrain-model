# DynaMix Channel Sweep Summary (Merged)

## Best Model Per Channel Set

| combo_name | channels           | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ---------- | ------------------ | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| perm4      | Fp2,F3,C4,T8,P8,O1 | 6          | L2LogisticRegression     | 137.22142857142856 | 31.030549432943584 | 0.5           |
| perm3      | F7,T7,Pz,O1        | 4          | SimpleLogisticRegression | 136.85714285714283 | 34.256546234837096 | 0.5           |
| informed1  | F7,Cz,P8,O2        | 4          | SimpleLogisticRegression | 134.82467532467533 | 27.17955971642844  | 0.5           |
| informed3  | Fz,FCz,Pz,Oz       | 4          | SimpleLogisticRegression | 133.9622655122655  | 32.9091337773134   | 0.5           |
| informed2  | F8,FC4,P8,O2       | 4          | SimpleLogisticRegression | 130.13730158730158 | 31.746529470304612 | 0.5           |
| perm2      | F3,C3,T8,P3,O2     | 5          | L1LogisticRegression     | 122.05238095238096 | 31.78798620578851  | 0.5           |
| perm1      | Fp1,FC4,T7,P4,O2   | 5          | SimpleLogisticRegression | 120.59877344877344 | 29.35115773989988  | 0.5           |

## Full Results

| combo_name | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ---------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| informed1  | SimpleLogisticRegression | 134.82467532467533 | 27.17955971642844  | 142.61317968569747 | 0.5           | 11                         |
| informed1  | L1LogisticRegression     | 129.60440115440116 | 29.72355277944691  | 138.75178104650854 | 0.5           | 11                         |
| informed1  | SupportVectorClassifier  | 129.32113997113996 | 25.524682405138964 | 153.88953174266106 | 0.5           | 11                         |
| informed1  | L2LogisticRegression     | 129.1492784992785  | 26.363263251825604 | 139.5548138984594  | 0.5           | 11                         |
| informed1  | ElasticNet               | 128.48304473304472 | 27.95037622839376  | 136.8684488654918  | 0.5           | 11                         |
| informed2  | SimpleLogisticRegression | 130.13730158730158 | 31.746529470304612 | 144.14263287412084 | 0.5           | 13                         |
| informed2  | L2LogisticRegression     | 126.1722222222222  | 31.719752724445613 | 140.90805761265258 | 0.5           | 13                         |
| informed2  | ElasticNet               | 123.9151515151515  | 33.73954458111596  | 134.60208812353588 | 0.5           | 13                         |
| informed2  | L1LogisticRegression     | 121.33412698412694 | 31.082343549012943 | 134.60214255363206 | 0.5           | 13                         |
| informed2  | SupportVectorClassifier  | 120.39249639249638 | 22.702221517370543 | 146.81500776301164 | 0.5           | 13                         |
| informed3  | SimpleLogisticRegression | 133.9622655122655  | 32.9091337773134   | 137.41504594558324 | 0.5           | 8                          |
| informed3  | SupportVectorClassifier  | 129.91038961038964 | 26.64788538166798  | 152.78207431098758 | 0.5           | 8                          |
| informed3  | L1LogisticRegression     | 128.31940836940836 | 34.086020114937654 | 133.32789474851958 | 0.5           | 8                          |
| informed3  | L2LogisticRegression     | 126.14956709956708 | 34.440281267513974 | 135.40802541211784 | 0.5           | 8                          |
| informed3  | ElasticNet               | 126.1484126984127  | 35.63445832591546  | 132.62534537308963 | 0.5           | 8                          |
| perm1      | SimpleLogisticRegression | 120.59877344877344 | 29.35115773989988  | 139.8243025639294  | 0.5           | 13                         |
| perm1      | L1LogisticRegression     | 118.82020202020202 | 29.296472188878973 | 131.8334397839498  | 0.5           | 13                         |
| perm1      | L2LogisticRegression     | 117.52012987012986 | 32.26991367301723  | 138.1798883144263  | 0.5           | 13                         |
| perm1      | ElasticNet               | 116.22900432900433 | 29.18438458613848  | 130.9028495483296  | 0.5           | 13                         |
| perm1      | SupportVectorClassifier  | 107.43073593073592 | 24.51576122005913  | 142.13036952803287 | 0.5           | 13                         |
| perm2      | L1LogisticRegression     | 122.05238095238096 | 31.78798620578851  | 129.66698089357388 | 0.5           | 15                         |
| perm2      | SimpleLogisticRegression | 119.3531746031746  | 36.61880228999773  | 141.0284506649116  | 0.5           | 15                         |
| perm2      | ElasticNet               | 119.22979797979797 | 28.71140637223544  | 130.8614558515502  | 0.5           | 15                         |
| perm2      | L2LogisticRegression     | 116.5404761904762  | 32.899920575474226 | 138.17744231868994 | 0.5           | 15                         |
| perm2      | SupportVectorClassifier  | 106.67972582972584 | 18.376046583266376 | 141.42798765062557 | 0.5           | 15                         |
| perm3      | SimpleLogisticRegression | 136.85714285714283 | 34.256546234837096 | 145.10108281676315 | 0.5           | 10                         |
| perm3      | L2LogisticRegression     | 136.25281385281386 | 32.57693716445478  | 144.37244566006476 | 0.5           | 10                         |
| perm3      | ElasticNet               | 136.1174603174603  | 31.923349398762586 | 143.84113197300783 | 0.5           | 10                         |
| perm3      | L1LogisticRegression     | 130.35317460317458 | 32.685681708321724 | 142.07831647366496 | 0.5           | 10                         |
| perm3      | SupportVectorClassifier  | 127.97698412698408 | 29.82100902660873  | 155.07757427665584 | 0.5           | 10                         |
| perm4      | L2LogisticRegression     | 137.22142857142856 | 31.030549432943584 | 145.88786365580776 | 0.5           | 13                         |
| perm4      | SimpleLogisticRegression | 133.98809523809524 | 28.281200172809864 | 148.0623822952981  | 0.5           | 13                         |
| perm4      | ElasticNet               | 132.77936507936508 | 30.47023540529047  | 141.9096595312723  | 0.5           | 13                         |
| perm4      | L1LogisticRegression     | 128.2183261183261  | 32.013955159302846 | 141.8369297533813  | 0.5           | 13                         |
| perm4      | SupportVectorClassifier  | 123.71471861471862 | 21.82827498273017  | 159.17506910686973 | 0.5           | 13                         |