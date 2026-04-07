# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name | channels           | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ---------- | ------------------ | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| perm4      | Fp2,F3,C4,T8,P8,O1 | 6          | L2LogisticRegression     | 137.22142857142856 | 31.030549432943584 | 0.5           |
| perm3      | F7,T7,Pz,O1        | 4          | SimpleLogisticRegression | 136.85714285714283 | 34.256546234837096 | 0.5           |
| perm2      | F3,C3,T8,P3,O2     | 5          | L1LogisticRegression     | 122.05238095238096 | 31.78798620578851  | 0.5           |
| perm1      | Fp1,FC4,T7,P4,O2   | 5          | SimpleLogisticRegression | 120.59877344877344 | 29.35115773989988  | 0.5           |

## Full Results

| combo_name | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ---------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| perm1      | SimpleLogisticRegression | 120.59877344877344 | 29.35115773989988  | 139.8243025639294  | 0.5           | 13                         |
| perm1      | L1LogisticRegression     | 118.82020202020202 | 29.296472188878973 | 131.83343978394979 | 0.5           | 13                         |
| perm1      | L2LogisticRegression     | 117.52012987012986 | 32.26991367301723  | 138.1798883144263  | 0.5           | 13                         |
| perm1      | ElasticNet               | 116.22900432900431 | 29.18438458613848  | 130.9028495483296  | 0.5           | 13                         |
| perm1      | SupportVectorClassifier  | 107.43073593073593 | 24.51576122005913  | 142.13036952803287 | 0.5           | 13                         |
| perm2      | L1LogisticRegression     | 122.05238095238096 | 31.78798620578851  | 129.66698089357388 | 0.5           | 15                         |
| perm2      | SimpleLogisticRegression | 119.3531746031746  | 36.61880228999773  | 141.0284506649116  | 0.5           | 15                         |
| perm2      | ElasticNet               | 119.22979797979797 | 28.711406372235437 | 130.8614558515502  | 0.5           | 15                         |
| perm2      | L2LogisticRegression     | 116.5404761904762  | 32.899920575474226 | 138.17744231868994 | 0.5           | 15                         |
| perm2      | SupportVectorClassifier  | 106.67972582972583 | 18.376046583266376 | 141.42798765062557 | 0.5           | 15                         |
| perm3      | SimpleLogisticRegression | 136.85714285714283 | 34.256546234837096 | 145.10108281676315 | 0.5           | 10                         |
| perm3      | L2LogisticRegression     | 136.25281385281386 | 32.57693716445478  | 144.37244566006476 | 0.5           | 10                         |
| perm3      | ElasticNet               | 136.1174603174603  | 31.923349398762582 | 143.84113197300783 | 0.5           | 10                         |
| perm3      | L1LogisticRegression     | 130.35317460317458 | 32.685681708321724 | 142.07831647366496 | 0.5           | 10                         |
| perm3      | SupportVectorClassifier  | 127.97698412698409 | 29.82100902660873  | 155.07757427665584 | 0.5           | 10                         |
| perm4      | L2LogisticRegression     | 137.22142857142856 | 31.030549432943584 | 145.88786365580776 | 0.5           | 13                         |
| perm4      | SimpleLogisticRegression | 133.98809523809524 | 28.281200172809864 | 148.0623822952981  | 0.5           | 13                         |
| perm4      | ElasticNet               | 132.77936507936508 | 30.47023540529047  | 141.9096595312723  | 0.5           | 13                         |
| perm4      | L1LogisticRegression     | 128.2183261183261  | 32.013955159302846 | 141.8369297533813  | 0.5           | 13                         |
| perm4      | SupportVectorClassifier  | 123.71471861471862 | 21.82827498273017  | 159.17506910686973 | 0.5           | 13                         |