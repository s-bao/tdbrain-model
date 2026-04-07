# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name | channels           | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ---------- | ------------------ | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| informed3  | Fz,FCz,Pz,Oz       | 4          | SimpleLogisticRegression | 142.2190476190476  | 30.411550828333773 | 0.5           |
| informed1  | F7,Cz,P8,O2        | 4          | SimpleLogisticRegression | 141.76031746031742 | 28.46857894947285  | 0.5           |
| perm4      | Fp2,F3,C4,T8,P8,O1 | 6          | SimpleLogisticRegression | 141.08340548340547 | 35.495909929120636 | 0.5           |
| perm3      | F7,T7,Pz,O1        | 4          | SimpleLogisticRegression | 140.52619047619046 | 33.1383538854351   | 0.5           |
| perm2      | F3,C3,T8,P3,O2     | 5          | SimpleLogisticRegression | 135.90634920634918 | 31.87995003778536  | 0.5           |
| informed2  | F8,FC4,P8,O2       | 4          | SimpleLogisticRegression | 133.07222222222222 | 31.72170555075226  | 0.5           |
| perm1      | Fp1,FC4,T7,P4,O2   | 5          | SimpleLogisticRegression | 124.44444444444446 | 31.320328270357624 | 0.5           |

## Full Results

| combo_name | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ---------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| informed1  | SimpleLogisticRegression | 141.76031746031742 | 28.46857894947285  | 148.69644767108682 | 0.5           | 12                         |
| informed1  | ElasticNet               | 138.49206349206347 | 27.580229517113874 | 144.06670083136797 | 0.5           | 12                         |
| informed1  | L1LogisticRegression     | 137.1595238095238  | 31.201682818527384 | 145.71337421910115 | 0.5           | 12                         |
| informed1  | L2LogisticRegression     | 136.56428571428572 | 30.586155148159627 | 145.80060320239    | 0.5           | 12                         |
| informed1  | SupportVectorClassifier  | 125.17106782106782 | 22.104274214871744 | 149.64679178841655 | 0.5           | 12                         |
| informed2  | SimpleLogisticRegression | 133.07222222222222 | 31.72170555075226  | 143.7530483672493  | 0.5           | 12                         |
| informed2  | L2LogisticRegression     | 127.67070707070707 | 31.795609780167183 | 140.42384461836608 | 0.5           | 12                         |
| informed2  | L1LogisticRegression     | 126.22698412698412 | 32.41796519092742  | 138.69704027383    | 0.5           | 12                         |
| informed2  | SupportVectorClassifier  | 124.95194805194804 | 20.79715171061596  | 151.2578911954378  | 0.5           | 12                         |
| informed2  | ElasticNet               | 121.56233766233763 | 33.25275222233932  | 135.9998060104516  | 0.5           | 12                         |
| informed3  | SimpleLogisticRegression | 142.2190476190476  | 30.411550828333773 | 143.2549303371641  | 0.5           | 11                         |
| informed3  | L2LogisticRegression     | 139.61190476190475 | 31.000020105407213 | 140.84927354854995 | 0.5           | 11                         |
| informed3  | L1LogisticRegression     | 138.4142857142857  | 33.60913110488872  | 140.17911174629893 | 0.5           | 11                         |
| informed3  | ElasticNet               | 136.19206349206345 | 33.7445272477419   | 137.81075552342375 | 0.5           | 11                         |
| informed3  | SupportVectorClassifier  | 120.27301587301586 | 21.572803783549446 | 143.32812344649784 | 0.5           | 11                         |
| perm1      | SimpleLogisticRegression | 124.44444444444446 | 31.320328270357624 | 140.0250131788021  | 0.5           | 12                         |
| perm1      | L1LogisticRegression     | 122.50555555555555 | 32.90319457939998  | 132.56814582718468 | 0.5           | 12                         |
| perm1      | ElasticNet               | 119.91825396825394 | 30.16146628389752  | 130.74638969096483 | 0.5           | 12                         |
| perm1      | L2LogisticRegression     | 117.78412698412698 | 35.15668359087062  | 137.2395437965047  | 0.5           | 12                         |
| perm1      | SupportVectorClassifier  | 113.87453102453101 | 24.99702787534002  | 142.71974284655286 | 0.5           | 12                         |
| perm2      | SimpleLogisticRegression | 135.90634920634918 | 31.87995003778536  | 145.58621923610488 | 0.5           | 14                         |
| perm2      | L2LogisticRegression     | 128.77301587301588 | 32.8864228483449   | 143.29518288523633 | 0.5           | 14                         |
| perm2      | L1LogisticRegression     | 127.96507936507935 | 33.40828783618108  | 139.03594389762517 | 0.5           | 14                         |
| perm2      | ElasticNet               | 126.11825396825395 | 34.58153192222958  | 138.22239773911681 | 0.5           | 14                         |
| perm2      | SupportVectorClassifier  | 123.81551226551227 | 24.14997575553393  | 156.81790473130187 | 0.5           | 14                         |
| perm3      | SimpleLogisticRegression | 140.52619047619046 | 33.1383538854351   | 146.3322050497192  | 0.5           | 11                         |
| perm3      | L1LogisticRegression     | 136.9178932178932  | 35.57455615726871  | 145.71346088372914 | 0.5           | 11                         |
| perm3      | L2LogisticRegression     | 135.25238095238095 | 33.50138360503565  | 144.05085325259316 | 0.5           | 11                         |
| perm3      | ElasticNet               | 133.1626984126984  | 33.0158260359098   | 144.55215544860664 | 0.5           | 11                         |
| perm3      | SupportVectorClassifier  | 126.045670995671   | 26.46248927555184  | 146.93102733052135 | 0.5           | 11                         |
| perm4      | SimpleLogisticRegression | 141.08340548340547 | 35.495909929120636 | 145.00062143448656 | 0.5           | 13                         |
| perm4      | L2LogisticRegression     | 136.0595238095238  | 34.4658981081461   | 143.50527100093743 | 0.5           | 13                         |
| perm4      | L1LogisticRegression     | 131.82186147186147 | 38.28889271219646  | 140.47817360033278 | 0.5           | 13                         |
| perm4      | ElasticNet               | 128.06948051948052 | 37.20364458921751  | 139.9873613106035  | 0.5           | 13                         |
| perm4      | SupportVectorClassifier  | 121.61515151515152 | 26.055280633820264 | 157.7939867537482  | 0.5           | 13                         |