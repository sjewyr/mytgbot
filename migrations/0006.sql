ALTER TABLE users_buildings
DROP CONSTRAINT users_buildings_building_id_fkey;

ALTER TABLE users_buildings
ADD CONSTRAINT users_buildings_building_id_fkey
  FOREIGN KEY (building_id)
  REFERENCES buildings(id)
  ON DELETE CASCADE;

ALTER TABLE users_buildings
DROP CONSTRAINT users_buildings_user_id_fkey;

ALTER TABLE users_buildings
ADD CONSTRAINT users_buildings_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES "users"(id)
  ON DELETE CASCADE;
