-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: veterinaria
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '84017d0b-b051-11f0-9927-644ed79ee9e4:1-175';

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `id_rol` int DEFAULT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'Cliente',
  `matricula` varchar(50) DEFAULT NULL,
  `especialidad` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Jose Smith','La Colonia','15245785','1pruebahtml@gmail.com','scrypt:32768:8:1$iV4LLfaBqH4bk1l8$2f788d01753cffe172aee2530fb2c93f0e170e8560e0cbb0c1641d0a327770968ecced5073631f7f6ded2f6be081ca1766b1a8f139634f7cfeae268d3457da53',NULL,'cliente',NULL,NULL),(2,'Santos Toledo','De La Uca 4 varas a mi yuca','19524863','2pruebahtml@gmail.com','scrypt:32768:8:1$36wWleZ2KMR7w1dG$cbdec2f486e0780b6878ade9f03c1082738f903831210c20b0494077ef1f40c973da8e90128f742532ba9253268364571dfed8ca1de42a232c3bd355552c0264',NULL,'cliente',NULL,NULL),(4,'Massiel Morales','ciudad sandino','15489652','vetmassiel@gmail.com','scrypt:32768:8:1$twx9y76l6NCPiAed$f63f16210f5b04783812a6a48a4a378dd9239d55fa378cc2d238a0cb6a3499f040cf40b542fc170641fa6d258ddb3e8a42607f0a9a234be445197b1b6539ce05',NULL,'veterinario',NULL,'General'),(5,'Sam Perez','ciudad sandino','15879623','1veterinarioprueba@gmail.com','scrypt:32768:8:1$pAfuzB0RKQ0lDUDQ$f334eef51332e742440cd228eccbb8109cbeabdecb8680d15d18bfa89692b41b35c3a6e33745de4fc9ed5211090ae2ae0cceef09868773f8b707eb155bb3cdbf',NULL,'veterinario',NULL,'General'),(6,'Sergio Amir','ciudad siniestra','78945875','3pruebahtml@gmail.com','scrypt:32768:8:1$2l0F55rf214uMD55$72f268ee64dc4995c947bdbde60cd7ce909a6424ef95ed3a4a5ffd3c0e3044fbb72ca7da6d4dff7a0e08acf9e2bd94e7ba6b74df77b8c963a3f8f0c849557641',NULL,'cliente',NULL,NULL),(7,'Eliezer plata','Ciudad sandino','78450759','eliezerplata@gmail.com','scrypt:32768:8:1$40KrX0gVNtoTigq7$180fb364bfe9d470fac54aceedd191c6c0d9ecba06b1f5093de28c253cbd7de7a6e83e62950ab82f77fc6c76572517f57050e38b55f082af9defb25dad1c56d1',NULL,'cliente',NULL,NULL);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-26 10:51:52
