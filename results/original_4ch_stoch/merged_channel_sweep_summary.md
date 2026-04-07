# DynaMix Channel Sweep Summary (Merged)

## Best Model Per Channel Set

| source_run                | combo_name   | channels    | n_channels | model_name               | mean_test_score    | std_test_score     | mean_baseline |
| ------------------------- | ------------ | ----------- | ---------- | ------------------------ | ------------------ | ------------------ | ------------- |
| original_4ch_stoch        | original_4ch | F7,P8,T7,O2 | 4          | SimpleLogisticRegression | 140.53412698412697 | 32.660269891764095 | 0.5           |
| original_4ch_stoch_round2 | original_4ch | F7,P8,T7,O2 | 4          | L2LogisticRegression     | 138.43492063492062 | 34.99995875173037  | 0.5           |

## Full Results

| source_run                | combo_name   | model_name               | mean_test_score    | std_test_score     | mean_train_score   | mean_baseline | n_input_features_post_corr |
| ------------------------- | ------------ | ------------------------ | ------------------ | ------------------ | ------------------ | ------------- | -------------------------- |
| original_4ch_stoch        | original_4ch | SimpleLogisticRegression | 140.53412698412697 | 32.660269891764095 | 150.14652693356035 | 0.5           | 11                         |
| original_4ch_stoch        | original_4ch | L1LogisticRegression     | 140.05714285714285 | 30.921849166210915 | 149.18503897616134 | 0.5           | 11                         |
| original_4ch_stoch        | original_4ch | L2LogisticRegression     | 137.18253968253967 | 31.39357820208716  | 148.24559961597114 | 0.5           | 11                         |
| original_4ch_stoch        | original_4ch | ElasticNet               | 135.6142857142857  | 30.811563314159088 | 147.3410077340413  | 0.5           | 11                         |
| original_4ch_stoch        | original_4ch | SupportVectorClassifier  | 121.70036075036076 | 26.250610924581174 | 140.45191536395836 | 0.5           | 11                         |
| original_4ch_stoch_round2 | original_4ch | L2LogisticRegression     | 138.43492063492062 | 34.99995875173037  | 143.02098695026237 | 0.5           | 11                         |
| original_4ch_stoch_round2 | original_4ch | SimpleLogisticRegression | 136.8051948051948  | 32.272363052333304 | 145.50329067714844 | 0.5           | 11                         |
| original_4ch_stoch_round2 | original_4ch | ElasticNet               | 132.87135642135644 | 36.59261434732913  | 142.3199181797809  | 0.5           | 11                         |
| original_4ch_stoch_round2 | original_4ch | L1LogisticRegression     | 130.57582972582972 | 33.10491002466101  | 142.86635055852446 | 0.5           | 11                         |
| original_4ch_stoch_round2 | original_4ch | SupportVectorClassifier  | 129.0997113997114  | 28.215953430012963 | 152.11535199845997 | 0.5           | 11                         |