# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name   | channels    | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ------------ | ----------- | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| original_4ch | F7,P8,T7,O2 | 4          | SimpleLogisticRegression | 140.53412698412697 | 32.660269891764095 | 0.5           |

## Full Results

| combo_name   | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ------------ | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| original_4ch | SimpleLogisticRegression | 140.53412698412697 | 32.660269891764095 | 150.14652693356035 | 0.5           | 11                         |
| original_4ch | L1LogisticRegression     | 140.05714285714285 | 30.921849166210915 | 149.18503897616134 | 0.5           | 11                         |
| original_4ch | L2LogisticRegression     | 137.18253968253967 | 31.39357820208716  | 148.24559961597114 | 0.5           | 11                         |
| original_4ch | ElasticNet               | 135.6142857142857  | 30.811563314159088 | 147.3410077340413  | 0.5           | 11                         |
| original_4ch | SupportVectorClassifier  | 121.70036075036076 | 26.250610924581178 | 140.45191536395836 | 0.5           | 11                         |