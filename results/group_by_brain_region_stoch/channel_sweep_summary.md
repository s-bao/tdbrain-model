# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name    | channels       | n_channels | model_name               | mean_test_score    | std_test_score    | mean_baseline |
| ------------- | -------------- | ---------- | ------------------------ | ------------------ | ----------------- | ------------- |
| occipital     | O1,Oz,O2       | 3          | SimpleLogisticRegression | 139.49999999999997 | 31.50828935070916 | 0.5           |
| central       | C3,Cz,C4       | 3          | SupportVectorClassifier  | 132.9699134199134  | 25.56070039817366 | 0.5           |
| frontal       | F7,F3,Fz,F4,F8 | 5          | SimpleLogisticRegression | 128.4385281385281  | 35.06463592560007 | 0.5           |
| frontocentral | FC3,FCz,FC4    | 3          | SimpleLogisticRegression | 125.93412698412698 | 32.08418484994613 | 0.5           |
| parietal      | P7,P3,Pz,P4,P8 | 5          | SimpleLogisticRegression | 125.53888888888889 | 32.54694517286782 | 0.5           |

## Full Results

| combo_name    | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ------------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| central       | SupportVectorClassifier  | 132.9699134199134  | 25.56070039817366  | 146.90761965462153 | 0.5           | 8                          |
| central       | SimpleLogisticRegression | 132.38730158730158 | 30.450159766096487 | 140.20627547053934 | 0.5           | 8                          |
| central       | L1LogisticRegression     | 129.6690476190476  | 32.77494137195362  | 137.9883555922089  | 0.5           | 8                          |
| central       | ElasticNet               | 123.26349206349205 | 37.06593119332114  | 138.86101477848555 | 0.5           | 8                          |
| central       | L2LogisticRegression     | 122.90317460317459 | 43.169968209425654 | 140.77877427228532 | 0.5           | 8                          |
| frontal       | SimpleLogisticRegression | 128.4385281385281  | 35.06463592560007  | 137.5210853012402  | 0.5           | 8                          |
| frontal       | L2LogisticRegression     | 126.1631313131313  | 35.840789877914446 | 135.32429733665694 | 0.5           | 8                          |
| frontal       | L1LogisticRegression     | 121.25995670995671 | 32.84469105593115  | 133.85864044393412 | 0.5           | 8                          |
| frontal       | SupportVectorClassifier  | 119.24502164502167 | 18.723120288768666 | 135.1123461745081  | 0.5           | 8                          |
| frontal       | ElasticNet               | 117.16385281385281 | 35.50929141943578  | 132.44044860095136 | 0.5           | 8                          |
| frontocentral | SimpleLogisticRegression | 125.93412698412698 | 32.08418484994613  | 134.12400831458172 | 0.5           | 8                          |
| frontocentral | L1LogisticRegression     | 123.12222222222222 | 30.726781060274224 | 129.160819920004   | 0.5           | 8                          |
| frontocentral | L2LogisticRegression     | 121.04920634920634 | 35.773937097554885 | 132.6053825257447  | 0.5           | 8                          |
| frontocentral | ElasticNet               | 120.37301587301589 | 34.09220172847282  | 128.38444054873077 | 0.5           | 8                          |
| frontocentral | SupportVectorClassifier  | 118.45757575757575 | 22.316921578134362 | 140.4988159948414  | 0.5           | 8                          |
| occipital     | SimpleLogisticRegression | 139.49999999999997 | 31.50828935070916  | 141.98264141740538 | 0.5           | 8                          |
| occipital     | L1LogisticRegression     | 133.31507936507936 | 31.7132268103407   | 138.95456946505462 | 0.5           | 8                          |
| occipital     | L2LogisticRegression     | 132.95995670995669 | 30.58739858443926  | 138.9799252332014  | 0.5           | 8                          |
| occipital     | ElasticNet               | 128.27380952380952 | 35.1131765785744   | 137.68076872576714 | 0.5           | 8                          |
| occipital     | SupportVectorClassifier  | 116.48520923520924 | 21.656288779254414 | 139.33429754443165 | 0.5           | 8                          |
| parietal      | SimpleLogisticRegression | 125.53888888888889 | 32.54694517286782  | 136.26729935009752 | 0.5           | 9                          |
| parietal      | ElasticNet               | 121.2738095238095  | 30.57972940884312  | 128.0050725294817  | 0.5           | 9                          |
| parietal      | L1LogisticRegression     | 120.85158730158727 | 30.376064971112562 | 128.14579879241293 | 0.5           | 9                          |
| parietal      | L2LogisticRegression     | 115.49329004329006 | 37.275909444659355 | 134.0879449613273  | 0.5           | 9                          |
| parietal      | SupportVectorClassifier  | 108.68318903318902 | 20.321713229141686 | 135.36987035012586 | 0.5           | 9                          |