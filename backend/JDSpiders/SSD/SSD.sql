use computer_accessories;
DROP TABLE IF EXISTS `ssd`;
CREATE TABLE `ssd` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` varchar(255) DEFAULT NULL,
  `praise_rate` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `link` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `interface` varchar(255) DEFAULT NULL,
  `total_capacity` varchar(255) DEFAULT NULL,
  `introduction` JSON,
  `Ptable_params` JSON,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate ssd; 