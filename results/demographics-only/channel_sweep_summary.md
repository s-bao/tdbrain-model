# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| source_run        | combo_name        | channels | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ----------------- | ----------------- | -------- | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| demographics-only | demographics_only |          | 0          | SimpleLogisticRegression | 128.61666666666667 | 29.683312643785104 | 0.5           |

## Full Results

| source_run        | combo_name        | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ----------------- | ----------------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| demographics-only | demographics_only | SimpleLogisticRegression | 128.61666666666667 | 29.683312643785104 | 129.4724812199048  | 0.5           | 3                          |
| demographics-only | demographics_only | L2LogisticRegression     | 126.80714285714286 | 31.97278710116428  | 130.0265890930584  | 0.5           | 3                          |
| demographics-only | demographics_only | ElasticNet               | 125.82460317460318 | 30.883037698884287 | 128.17467105212884 | 0.5           | 3                          |
| demographics-only | demographics_only | L1LogisticRegression     | 125.01587301587303 | 31.0187749450711   | 128.1429763398556  | 0.5           | 3                          |
| demographics-only | demographics_only | SupportVectorClassifier  | 116.14487734487733 | 23.606611215964552 | 124.59195667327907 | 0.5           | 3                          |