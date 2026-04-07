# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name    | channels       | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ------------- | -------------- | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| occipital     | O1,Oz,O2       | 3          | SimpleLogisticRegression | 139.14761904761906 | 29.871927050312117 | 0.5           |
| central       | C3,Cz,C4       | 3          | SimpleLogisticRegression | 130.09682539682538 | 31.441052075367104 | 0.5           |
| frontal       | F7,F3,Fz,F4,F8 | 5          | SimpleLogisticRegression | 128.04841269841268 | 31.474529679067782 | 0.5           |
| parietal      | P7,P3,Pz,P4,P8 | 5          | SimpleLogisticRegression | 126.77142857142859 | 33.01052284184183  | 0.5           |
| frontocentral | FC3,FCz,FC4    | 3          | SimpleLogisticRegression | 125.7436507936508  | 27.55523474458485  | 0.5           |

## Full Results

| combo_name    | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ------------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| central       | SimpleLogisticRegression | 130.09682539682538 | 31.441052075367104 | 136.44928350654206 | 0.5           | 8                          |
| central       | SupportVectorClassifier  | 126.79170274170274 | 25.260889813500558 | 142.97095606935957 | 0.5           | 8                          |
| central       | L1LogisticRegression     | 123.431746031746   | 32.00448192347004  | 131.26531105507544 | 0.5           | 8                          |
| central       | ElasticNet               | 123.40281385281384 | 33.223562918801136 | 136.23370653489584 | 0.5           | 8                          |
| central       | L2LogisticRegression     | 123.26587301587303 | 33.55990153525009  | 139.03838607141284 | 0.5           | 8                          |
| frontal       | SimpleLogisticRegression | 128.04841269841268 | 31.474529679067782 | 133.45933864678798 | 0.5           | 6                          |
| frontal       | L1LogisticRegression     | 123.59920634920633 | 31.14608168790983  | 130.17442086627977 | 0.5           | 6                          |
| frontal       | ElasticNet               | 122.91551226551228 | 32.74690443289277  | 131.039118295188   | 0.5           | 6                          |
| frontal       | L2LogisticRegression     | 122.91190476190476 | 36.983690465098825 | 133.19811175302524 | 0.5           | 6                          |
| frontal       | SupportVectorClassifier  | 112.49025974025973 | 24.359948571758693 | 128.87452705906455 | 0.5           | 6                          |
| frontocentral | SimpleLogisticRegression | 125.7436507936508  | 27.55523474458485  | 132.56118282632644 | 0.5           | 6                          |
| frontocentral | L2LogisticRegression     | 123.67893217893217 | 31.44916871738423  | 131.5101650921837  | 0.5           | 6                          |
| frontocentral | L1LogisticRegression     | 122.57063492063493 | 29.27009712856874  | 128.53541122627652 | 0.5           | 6                          |
| frontocentral | ElasticNet               | 120.72344877344877 | 31.813259769470445 | 129.11934643122794 | 0.5           | 6                          |
| frontocentral | SupportVectorClassifier  | 113.84610389610388 | 21.832309740959435 | 132.03311271518842 | 0.5           | 6                          |
| occipital     | SimpleLogisticRegression | 139.14761904761906 | 29.871927050312117 | 142.2639125970242  | 0.5           | 8                          |
| occipital     | L1LogisticRegression     | 134.9515873015873  | 32.76339262148441  | 139.4470006797941  | 0.5           | 8                          |
| occipital     | L2LogisticRegression     | 133.1325396825397  | 26.617030181190664 | 140.16699626920666 | 0.5           | 8                          |
| occipital     | ElasticNet               | 131.1142857142857  | 27.737053866956437 | 137.9869077615839  | 0.5           | 8                          |
| occipital     | SupportVectorClassifier  | 125.77950937950938 | 21.53742383253555  | 142.37581522620727 | 0.5           | 8                          |
| parietal      | SimpleLogisticRegression | 126.77142857142859 | 33.01052284184183  | 135.24432261660382 | 0.5           | 9                          |
| parietal      | ElasticNet               | 120.0916305916306  | 33.68181434889851  | 131.22294037076517 | 0.5           | 9                          |
| parietal      | L1LogisticRegression     | 119.23333333333332 | 30.22732845852377  | 129.43870232033652 | 0.5           | 9                          |
| parietal      | L2LogisticRegression     | 118.96904761904763 | 33.79087748011911  | 135.2033886767949  | 0.5           | 9                          |
| parietal      | SupportVectorClassifier  | 105.28261183261183 | 21.260722440205942 | 136.87130677888155 | 0.5           | 9                          |