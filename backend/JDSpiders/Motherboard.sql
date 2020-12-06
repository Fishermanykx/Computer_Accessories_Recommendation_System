use computer_accessories;
DROP TABLE IF EXISTS `motherboard`;
CREATE TABLE `motherboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `comment_num` varchar(255) DEFAULT NULL,
  `praise_rate` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `link` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `form_factor` varchar(255) DEFAULT NULL,
  `platform` varchar(255) DEFAULT NULL, 
  `introduction` JSON,
  `Ptable_params` JSON,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
truncate motherboard; 