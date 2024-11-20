-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: MySQL
-- Generated at: 2024-11-20T18:18:09.357Z

DROP DATABASE IF EXISTS steamdatabase;
CREATE DATABASE steamdatabase;

-- Connect to the database
USE steamdatabase;

-- Create tables
CREATE TABLE `Games` (
  `id` INT PRIMARY KEY,
  `name` VARCHAR(255),
  `type` VARCHAR(255),
  `price_initial` INT,
  `price_final` INT,
  `currency` VARCHAR(255),
  `tiny_image` VARCHAR(2083), -- Longer for URL storage
  `metascore` INT,
  `platforms_windows` TINYINT(1),
  `platforms_mac` TINYINT(1),
  `platforms_linux` TINYINT(1),
  `streamingvideo` TINYINT(1),
  `controller_support` VARCHAR(255)
);

CREATE TABLE `Achievements` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `app_id` INT NOT NULL,
  `name` VARCHAR(255),
  `percent` FLOAT,
  INDEX `idx_achievements_app_id` (`app_id`)
);

CREATE TABLE `PlayerCounts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `app_id` INT NOT NULL,
  `current_player_count` INT,
  INDEX `idx_playercounts_app_id` (`app_id`)
);

CREATE TABLE `Users` (
  `id` VARCHAR(255) PRIMARY KEY,
  `display_name` VARCHAR(255),
  `profile_url` VARCHAR(2083)
);

CREATE TABLE `UserOwnedGames` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` VARCHAR(255) NOT NULL,
  `app_id` INT NOT NULL,
  `playtime_forever` INT,
  `playtime_2weeks` INT,
  INDEX `idx_userownedgames_user_id` (`user_id`),
  INDEX `idx_userownedgames_app_id` (`app_id`)
);

CREATE TABLE `UserGameStatistics` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` VARCHAR(255) NOT NULL,
  `app_id` INT NOT NULL,
  `stat_name` VARCHAR(255),
  `stat_value` INT,
  INDEX `idx_usergamestatistics_user_id` (`user_id`),
  INDEX `idx_usergamestatistics_app_id` (`app_id`)
);

CREATE TABLE `UserAchievementStatistics` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` VARCHAR(255) NOT NULL,
  `app_id` INT NOT NULL,
  `achievement_name` VARCHAR(255),
  `achieved` TINYINT(1),
  INDEX `idx_userachievementstatistics_user_id` (`user_id`),
  INDEX `idx_userachievementstatistics_app_id` (`app_id`)
);

-- Add foreign keys
ALTER TABLE `Achievements`
  ADD FOREIGN KEY (`app_id`) REFERENCES `Games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `PlayerCounts`
  ADD FOREIGN KEY (`app_id`) REFERENCES `Games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `UserOwnedGames`
  ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD FOREIGN KEY (`app_id`) REFERENCES `Games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `UserGameStatistics`
  ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD FOREIGN KEY (`app_id`) REFERENCES `Games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `UserAchievementStatistics`
  ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD FOREIGN KEY (`app_id`) REFERENCES `Games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
