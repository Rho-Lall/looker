include: "customer_orders.semantic.view"

view: +customer_orders {
  #########################
  ## IDS
  #########################

  # PRIMARY KEY

  dimension: order_id {
    group_label: "IDs"
    # hidden: yes
  }

  dimension: customer_id {
    group_label: "IDs"
    # hidden: yes
  }

  dimension: product_id {
    group_label: "IDs"
    # hidden: yes
  }

  #########################
  ## DATES & TIMESTAMPS
  #########################

  dimension_group: order_date {
    label: "Order"
    group_label: " Order"
    can_filter: no
  }

  dimension_group: order_date_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Order"
    group_label: " Order"
    type: time
    sql: ${order_date_raw};;
  }

  dimension_group: shipped_date {
    label: "Shipped"
    group_label: " Shipped"
    can_filter: no
  }

  dimension_group: shipped_date_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Shipped"
    group_label: " Shipped"
    type: time
    sql: ${shipped_date_raw};;
  }

  #########################
  ## METRICS
  #########################

  measure: order_amount_total {
  value_format: "$#,##0.00"
  }

  measure: tax_amount_total {
  value_format: "$#,##0.00"
  }

  measure: discount_amount_total {
  value_format: "$#,##0.00"
  }

  measure: shipping_cost_total {
  value_format: "$#,##0.00"
  }

  measure: count {
    hidden: yes
  }

  #########################
  ## MEASURE DIMS
  #########################

  dimension: order_amount {
    group_label: "Measure Dims"
    hidden: yes
  }

  dimension: tax_amount {
    group_label: "Measure Dims"
    hidden: yes
  }

  dimension: discount_amount {
    group_label: "Measure Dims"
    hidden: yes
  }

  dimension: shipping_cost {
    group_label: "Measure Dims"
    hidden: yes
  }

  #########################
  ## DIMENSIONS
  #########################

  suggestions: yes

  dimension: customer_name {
    can_filter: no
  }

  dimension: customer_name_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Customer Name"
    type: string
    case_sensitive: no
    sql: ${customer_name};;
  }

  dimension: product_category {
    can_filter: no
  }

  dimension: product_category_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Product Category"
    type: string
    case_sensitive: no
    sql: ${product_category};;
  }

  dimension: order_status {
    can_filter: no
  }

  dimension: order_status_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Order Status"
    type: string
    case_sensitive: no
    sql: ${order_status};;
  }

  dimension: payment_method {
    can_filter: no
  }

  dimension: payment_method_filter {
    view_label: "FILTERS"
    # view_label: ""
    label: "Payment Method"
    type: string
    case_sensitive: no
    sql: ${payment_method};;
  }

}