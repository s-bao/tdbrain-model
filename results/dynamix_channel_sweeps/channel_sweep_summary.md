# DynaMix Channel Sweep Summary

## Best Model Per Channel Set

| combo_name | channels    | n_channels | model_name | mean_test_score   | std_test_score   | mean_baseline |
| ---------- | ----------- | ---------- | ---------- | ----------------- | ---------------- | ------------- |
| original   | F7,P8,T7,O2 | 4          | ElasticNet | 139.5769841269841 | 35.2932395188076 | 0.5           |

## Full Results

| combo_name | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ---------- | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| original   | ElasticNet               | 139.5769841269841  | 35.2932395188076   | 146.77456147670216 | 0.5           | 11                         |
| original   | L2LogisticRegression     | 138.00281385281383 | 32.098549128371815 | 147.48604098995278 | 0.5           | 11                         |
| original   | SimpleLogisticRegression | 130.73730158730157 | 30.06206583625217  | 144.52479608000948 | 0.5           | 11                         |
| original   | L1LogisticRegression     | 127.08095238095237 | 32.76049081020418  | 139.2820495339873  | 0.5           | 11                         |
| original   | SupportVectorClassifier  | 126.36277056277056 | 27.396457580995275 | 147.13800972564601 | 0.5           | 11                         |