import json

from great_expectations.core import ensure_json_serializable
from great_expectations.core.metric import ValidationMetricIdentifier
from great_expectations.data_context.store.database_store_backend import DatabaseStoreBackend
from great_expectations.data_context.store.store import Store
from great_expectations.util import load_class


class MetricStore(Store):
    _key_class = ValidationMetricIdentifier

    def __init__(self, store_backend=None):
        if store_backend is not None:
            store_backend_module_name = store_backend.get("module_name", "great_expectations.data_context.store")
            store_backend_class_name = store_backend.get("class_name", "InMemoryStoreBackend")
            store_backend_class = load_class(store_backend_class_name, store_backend_module_name)

            if issubclass(store_backend_class, DatabaseStoreBackend):
                # Provide defaults for this common case
                store_backend["table_name"] = store_backend.get("table_name", "ge_metrics")
                store_backend["key_columns"] = store_backend.get(
                    "key_columns", [
                        "run_id",
                        "expectation_suite_identifier",
                        "metric_name",
                        "metric_kwargs_id",
                    ]
                )

        super(MetricStore, self).__init__(store_backend=store_backend)

    # noinspection PyMethodMayBeStatic
    def _validate_value(self, value):
        # Values must be json serializable since they must be inputs to expectation configurations
        ensure_json_serializable(value)

    def serialize(self, key, value):
        return json.dumps({"value": value})

    def deserialize(self, key, value):
        if value:
            return json.loads(value)["value"]


class EvaluationParameterStore(MetricStore):

    def __init__(self, store_backend=None):
        if store_backend is not None:
            store_backend_module_name = store_backend.get("module_name", "great_expectations.data_context.store")
            store_backend_class_name = store_backend.get("class_name", "InMemoryStoreBackend")
            store_backend_class = load_class(store_backend_class_name, store_backend_module_name)

            if issubclass(store_backend_class, DatabaseStoreBackend):
                # Provide defaults for this common case
                store_backend["table_name"] = store_backend.get("table_name", "ge_evaluation_parameters")
        super(EvaluationParameterStore, self).__init__(store_backend=store_backend)

    def get_bind_params(self, run_id):
        params = {}
        for k in self._store_backend.list_keys((run_id,)):
            key = self.tuple_to_key(k)
            params[key.to_evaluation_parameter_urn()] = self.get(key)
        return params
