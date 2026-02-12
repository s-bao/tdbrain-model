import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def plot_permutation_results(perm_plot_data, title_suffix):
    for model_name, (cv_scores, perm_scores_list, p_values) in perm_plot_data.items():

        cv_score = np.mean(cv_scores)
        perm_scores = np.concatenate(perm_scores_list)
        p_value = np.mean(p_values)

        plt.figure(figsize=(5,3))
        plt.hist(perm_scores, bins=20, density=True, label="Permutation scores")

        plt.axvline(
            cv_score,
            ls="--",
            color="r",
            label=f"Mean score on original data = {cv_score:.2f}\n(p = {p_value:.3f})"
        )

        plt.legend(fontsize=8)
        plt.xlabel("Accuracy score")
        plt.ylabel("Probability density")
        plt.title(f"Permutation Scores: {model_name} ({title_suffix})")

        plt.show()


def get_logreg_feature_importance(model):
    log_reg_model = model.named_steps['logisticregression']

    # get the preprocessed feature names
    preprocessor = model.named_steps['columntransformer']
    feature_names = preprocessor.get_feature_names_out()

    # get coefficients
    coefs = log_reg_model.coef_[0]  # binary classification

    # put in dataframe
    feat_imp = pd.DataFrame({
        'feature': feature_names,
        'importance': np.abs(coefs),
        'coef': coefs
    }).sort_values(by='importance', ascending=False)

    return feat_imp


def plot_logreg_feature_importance(feat_imp):
    plt.figure(figsize=(6, 4))
    colors = ['green' if c > 0 else 'red' for c in feat_imp['coef']]
    plt.barh(feat_imp['feature'], feat_imp['coef'], color=colors)
    plt.gca().invert_yaxis()
    plt.xlabel('Coefficient magnitude (importance)')
    plt.title('Feature Importance for Logistic Regression')
    plt.show()


def plot_confusion_matrix(model, X_test, y_test, class_labels, title="Confusion Matrix"):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    # normalize
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    disp = ConfusionMatrixDisplay(confusion_matrix=cm_norm, display_labels=class_labels)
    disp.plot(values_format='.3f', cmap=plt.cm.Blues)
    plt.title(title)
    plt.show()