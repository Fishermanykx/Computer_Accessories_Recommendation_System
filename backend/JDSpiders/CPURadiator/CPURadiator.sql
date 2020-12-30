use computer_accessories;
DROP TABLE IF EXISTS `cpu_radiator`;
CREATE TABLE `cpu_radiator` (
  `name` varchar(255) DEFAULT NULL,
  `comment_num` varchar(255) DEFAULT NULL,
  `praise_rate` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `link` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  PRIMARY KEY (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate cpu_radiator; 