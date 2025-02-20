import pytest
import joblib
import os
import tensorflow.keras
from fxincome.utils import ModelAttr, JsonModel


class TestModel:
    @pytest.fixture(scope='class')
    def global_data(self):
        os.chdir('../fxincome')
        lstm_name = 'Checkpoint-10-SEQ-1-PRED-20210903-1639.model'
        lstm_features = [
            'close',  # scale
            'amount',  # scale
            't10y',  # scale
            'fr007_5y',  # scale
            'pct_chg',
            'avg_chg_10',
            'spread_t10y',
            'spread_fr007',
            'spread_fr007_5y',
            'spread_usdcny'  # scale
        ]
        lstm_scaled_feats = ['close', 'amount', 't10y', 'fr007_5y', 'spread_usdcny']
        lstm_stats = joblib.load('ml/models/stats-10-SEQ-1-PRED-20210903-1639.pkl')
        xgb_name = '0.626-1d_fwd-XGB-20210618-1454-v2016.pkl'
        xgb_features = ['close', 'pct_chg', 'avg_chg_5', 'avg_chg_10', 'fr007_chg_5', 'spread_t1y',
                        'spread_fr007', 'spread_usdcny', 'usdcny_chg_5']
        rfc_name = '0.605-1d_fwd-RFC-20210619-1346-v2018.pkl'
        rfc_features = xgb_features
        labels = ['target']
        lstm_model = ModelAttr(lstm_name, lstm_features, labels, lstm_scaled_feats, lstm_stats)
        xgb_model = ModelAttr(xgb_name, xgb_features, labels)
        rfc_model = ModelAttr(rfc_name, rfc_features, labels)
        return {
            'lstm_name': lstm_name,
            'lstm_features': lstm_features,
            'lstm_scaled_feats': lstm_scaled_feats,
            'lstm_stats': lstm_stats,
            'xgb_name': xgb_name,
            'xgb_features': xgb_features,
            'rfc_name': rfc_name,
            'labels': labels,
            'lstm_model': lstm_model,
            'xgb_model': xgb_model,
            'rfc_model': rfc_model
        }

    def test_save_attr(self, global_data):
        lstm_model = global_data['lstm_model']
        JsonModel.save_attr(lstm_model)
        model = JsonModel.load_attr(lstm_model.name)
        assert lstm_model.name == model.name
        assert lstm_model.features == model.features
        assert lstm_model.scaled_feats == model.scaled_feats
        assert lstm_model.stats == model.stats
        JsonModel.save_attr(global_data['xgb_model'])
        JsonModel.save_attr(global_data['rfc_model'])

    def test_load_attr(self, global_data):
        xgb_model = global_data['xgb_model']
        model = JsonModel.load_attr(xgb_model.name)
        assert xgb_model.name == model.name
        assert xgb_model.features == model.features
        assert JsonModel.load_attr('Non-Exists') is None

    def test_load_plain_models(self, global_data):
        plain_names = [global_data['xgb_name'], global_data['rfc_name']]
        plain_dict = JsonModel.load_plain_models(plain_names)
        xgb_model = joblib.load(JsonModel.model_path + global_data['xgb_name'])
        plain_model = plain_dict[global_data['xgb_model']]
        assert plain_model.get_params()['gamma'] == xgb_model.get_params()['gamma']

    def test_load_nn_models(self, global_data):
        nn_names = [global_data['lstm_name']]
        nn_dict = JsonModel.load_nn_models(nn_names)
        lstm_model = tensorflow.keras.models.load_model(JsonModel.model_path + global_data['lstm_name'])
        nn_model = nn_dict[global_data['lstm_model']]
        assert nn_model.summary() == lstm_model.summary()