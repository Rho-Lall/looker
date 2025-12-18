connection: "sample_connection"

include: "/views/*.view.lkml"
include: "/explores/*.explore.lkml"

datagroup: model_default_datagroup {
  sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: model_default_datagroup