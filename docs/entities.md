# Market <entity>

A `market` is an entity that represents a related group of stores. At start markets will be only related to political administrative levels like the ones related in the `conventions.md ## Political Administrative Levels` section.

For example, if we have a locality_a and locality_b belonging to a certain aal2_x high level area:

Represented as:

- aal2_x
    + locality_a (12 stores)
    + locality_b (20 stores)

We will create a market for locality_b and locality_a stores will be included in aal2_x.

The process to create those markets will be located in the processes directory behind the root will be executed once a week unless its manually executed.

# Store <datastore entity>

Below the database `store` entity we will have different entities. Those are listed on the same <datastore entity> for query performance reasons. As we will usually list both entities at the same time.

## Store <entity>

## StoreGroup <entity>


