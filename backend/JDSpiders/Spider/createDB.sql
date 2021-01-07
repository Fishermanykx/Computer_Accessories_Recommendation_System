CREATE DATABASE IF NOT EXISTS computer_accessories;
USE computer_accessories;

DROP TABLE IF EXISTS `cpu`;
CREATE TABLE `cpu` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `clock_speed` varchar(255) DEFAULT NULL,
  `core_num` varchar(255) DEFAULT NULL,
  `TDP` INT DEFAULT 0,
  `socket` varchar(255) DEFAULT NULL,
  `have_core_graphics_card` varchar(255) DEFAULT NULL,
  `have_cpu_fan` varchar(255) DEFAULT NULL,
  `generation` INT DEFAULT 0,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate cpu; 

DROP TABLE IF EXISTS `motherboard`;
CREATE TABLE `motherboard` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `form_factor` varchar(255) DEFAULT NULL,
  `platform` varchar(255) DEFAULT NULL, 
  `cpu_socket` varchar(255) DEFAULT NULL, 
  `m2_num` INT DEFAULT 0, 
  `slot_num` INT DEFAULT 0, 
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate motherboard; 

DROP TABLE IF EXISTS `graphics_card`;
CREATE TABLE `graphics_card` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `card_length` float DEFAULT 0,
  `rgb` varchar(255) DEFAULT NULL,
  `card_type` varchar(255) DEFAULT NULL,
  `generation` INT DEFAULT 0,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate graphics_card; 

DROP TABLE IF EXISTS `memory`;
CREATE TABLE `memory` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `frequency` varchar(255) DEFAULT NULL,
  `total_capacity` INT DEFAULT 0,
  `memory_num` varchar(255) DEFAULT NULL,
  `appearance` varchar(255) DEFAULT NULL,
  `ddr_gen` varchar(255) DEFAULT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate memory; 

DROP TABLE IF EXISTS `cpu_radiator`;
CREATE TABLE `cpu_radiator` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `height` INT DEFAULT 0,
  `socket` varchar(255) DEFAULT NULL,
  `radiator_size` INT DEFAULT 0,
  `rgb` varchar(255) DEFAULT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate cpu_radiator; 

DROP TABLE IF EXISTS `ssd`;
CREATE TABLE `ssd` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `interface` varchar(255) DEFAULT NULL,
  `total_capacity` FLOAT DEFAULT 0,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate ssd; 

DROP TABLE IF EXISTS `hdd`;
CREATE TABLE `hdd` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `size` varchar(255) DEFAULT NULL,
  `rotating_speed` varchar(255) DEFAULT NULL,
  `total_capacity` FLOAT DEFAULT 0,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate hdd; 

DROP TABLE IF EXISTS `power_supply`;
CREATE TABLE `power_supply` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `power` INT DEFAULT 0,
  `size` varchar(255) DEFAULT NULL,
  `modularization` varchar(255) DEFAULT NULL,
  `transfer_efficiency` varchar(255) DEFAULT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate power_supply; 

DROP TABLE IF EXISTS `computer_case`;
CREATE TABLE `computer_case` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` INT DEFAULT 100,
  `praise_rate` INT DEFAULT 90,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `max_form_factor` varchar(255) DEFAULT NULL,
  `max_card_len` INT DEFAULT 0,
  `max_radiator_height` INT DEFAULT 0,
  `supported_radiator` varchar(255) DEFAULT NULL,
  `has_transparent_side_panel` INT DEFAULT 0,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate computer_case; 

DROP TABLE IF EXISTS `board_u_suit`;
CREATE TABLE `board_u_suit` (
  `id` int(11) DEFAULT 0,
  `name` varchar(255) DEFAULT NULL,
  `board` varchar(255) DEFAULT NULL,
  `cpu` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `link` varchar(255) NOT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  `title_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate board_u_suit; 