-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: hotel_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `kamar`
--

DROP TABLE IF EXISTS `kamar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kamar` (
  `id_kamar` int(11) NOT NULL AUTO_INCREMENT,
  `nomor_kamar` varchar(10) NOT NULL,
  `tipe_kamar` varchar(50) NOT NULL,
  `tarif_per_malam` decimal(12,2) NOT NULL CHECK (`tarif_per_malam` > 0),
  `status` enum('Tersedia','Terisi') NOT NULL DEFAULT 'Tersedia',
  PRIMARY KEY (`id_kamar`),
  UNIQUE KEY `nomor_kamar` (`nomor_kamar`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kamar`
--

LOCK TABLES `kamar` WRITE;
/*!40000 ALTER TABLE `kamar` DISABLE KEYS */;
INSERT INTO `kamar` VALUES (1,'101','Standard Room',500000.00,'Tersedia'),(2,'102','Standard Room',500000.00,'Tersedia'),(3,'103','Standard Room',500000.00,'Tersedia'),(4,'104','Standard Room',500000.00,'Tersedia'),(5,'105','Standard Room',500000.00,'Tersedia'),(6,'106','Standard Room',500000.00,'Tersedia'),(7,'107','Standard Room',500000.00,'Tersedia'),(8,'108','Economy Room',400000.00,'Tersedia'),(9,'109','Economy Room',400000.00,'Tersedia'),(10,'110','Economy Room',400000.00,'Tersedia'),(11,'201','Deluxe Room',800000.00,'Tersedia'),(12,'202','Deluxe Room',800000.00,'Tersedia'),(13,'203','Deluxe Room',800000.00,'Tersedia'),(14,'204','Deluxe Room',800000.00,'Tersedia'),(15,'205','Deluxe Room',800000.00,'Tersedia'),(16,'206','Deluxe Room',800000.00,'Tersedia'),(17,'207','Twin Room',600000.00,'Tersedia'),(18,'208','Twin Room',600000.00,'Tersedia'),(19,'209','Superior Room',650000.00,'Tersedia'),(20,'210','Superior Room',650000.00,'Tersedia'),(21,'211','Superior Room',650000.00,'Tersedia'),(22,'301','Suite Room',1500000.00,'Tersedia'),(23,'302','Suite Room',1500000.00,'Tersedia'),(24,'303','Suite Room',1500000.00,'Tersedia'),(25,'304','Family Room',1200000.00,'Tersedia'),(26,'305','Family Room',1200000.00,'Tersedia'),(27,'306','Junior Suite',1000000.00,'Tersedia'),(28,'307','Junior Suite',1000000.00,'Tersedia'),(29,'401','Executive Suite',2500000.00,'Tersedia'),(30,'402','Executive Suite',2500000.00,'Tersedia'),(31,'403','Honeymoon Suite',3000000.00,'Tersedia'),(32,'404','Honeymoon Suite',3000000.00,'Tersedia'),(33,'405','Ocean View Suite',3500000.00,'Tersedia'),(34,'406','Ocean View Suite',3500000.00,'Tersedia'),(35,'501','Presidential Suite',4500000.00,'Tersedia'),(36,'502','Presidential Suite',4500000.00,'Tersedia'),(37,'503','Penthouse Suite',7500000.00,'Tersedia'),(38,'504','Penthouse Suite',7500000.00,'Tersedia'),(39,'V01','Private Villa',6000000.00,'Tersedia'),(40,'V02','Private Villa',6000000.00,'Tersedia'),(41,'V03','Private Villa',6000000.00,'Tersedia');
/*!40000 ALTER TABLE `kamar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pembayaran`
--

DROP TABLE IF EXISTS `pembayaran`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pembayaran` (
  `id_pembayaran` int(11) NOT NULL AUTO_INCREMENT,
  `id_reservasi` int(11) NOT NULL,
  `tgl_bayar` date NOT NULL,
  `total_biaya` decimal(14,2) NOT NULL,
  `metode` enum('Tunai','Transfer','Kartu') NOT NULL DEFAULT 'Tunai',
  PRIMARY KEY (`id_pembayaran`),
  KEY `id_reservasi` (`id_reservasi`),
  CONSTRAINT `pembayaran_ibfk_1` FOREIGN KEY (`id_reservasi`) REFERENCES `reservasi` (`id_reservasi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pembayaran`
--

LOCK TABLES `pembayaran` WRITE;
/*!40000 ALTER TABLE `pembayaran` DISABLE KEYS */;
/*!40000 ALTER TABLE `pembayaran` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pengguna`
--

DROP TABLE IF EXISTS `pengguna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pengguna` (
  `id_pengguna` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `password_hash` char(64) NOT NULL,
  `role` enum('admin','resepsionis') NOT NULL DEFAULT 'resepsionis',
  PRIMARY KEY (`id_pengguna`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pengguna`
--

LOCK TABLES `pengguna` WRITE;
/*!40000 ALTER TABLE `pengguna` DISABLE KEYS */;
/*!40000 ALTER TABLE `pengguna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservasi`
--

DROP TABLE IF EXISTS `reservasi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reservasi` (
  `id_reservasi` int(11) NOT NULL AUTO_INCREMENT,
  `id_tamu` int(11) NOT NULL,
  `id_kamar` int(11) NOT NULL,
  `tgl_checkin` date NOT NULL,
  `tgl_checkout` date NOT NULL,
  `status` enum('Check-In','Check-Out') NOT NULL DEFAULT 'Check-In',
  PRIMARY KEY (`id_reservasi`),
  KEY `id_tamu` (`id_tamu`),
  KEY `id_kamar` (`id_kamar`),
  CONSTRAINT `reservasi_ibfk_1` FOREIGN KEY (`id_tamu`) REFERENCES `tamu` (`id_tamu`),
  CONSTRAINT `reservasi_ibfk_2` FOREIGN KEY (`id_kamar`) REFERENCES `kamar` (`id_kamar`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservasi`
--

LOCK TABLES `reservasi` WRITE;
/*!40000 ALTER TABLE `reservasi` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservasi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tamu`
--

DROP TABLE IF EXISTS `tamu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tamu` (
  `id_tamu` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `alamat` varchar(255) DEFAULT NULL,
  `telepon` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_tamu`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tamu`
--

LOCK TABLES `tamu` WRITE;
/*!40000 ALTER TABLE `tamu` DISABLE KEYS */;
INSERT INTO `tamu` VALUES (1,'Budi Santoso','Jl. Merdeka No. 12, Jakarta','081234567890','budi.santoso@email.com'),(2,'Siti Rahmawati','Jl. Sudirman No. 45, Bandung','085712345679','siti.rahma@email.com'),(3,'Kevin Pratama','Jl. Ahmad Yani No. 88, Surabaya','082198765432','kevin.p@email.com'),(4,'Dewi Lestari','Jl. Diponegoro No. 10, Yogyakarta','08817626412','dewi.l@email.com'),(5,'Reza Firmansyah','Jl. Asia Afrika No. 5, Bandung','081399887766','reza.firmansyah@email.com'),(6,'Rina Marlina','Jl. Gajah Mada No. 14, Semarang','081566778899','rina.marlina@email.com'),(7,'Dimas Anggara','Jl. Malioboro No. 20, Yogyakarta','081899001122','dimas.a@email.com'),(8,'Maya Sari','Jl. Pahlawan No. 7, Malang','081277665544','maya.sari@email.com'),(9,'Fajar Nugraha','Jl. Riau No. 33, Pekanbaru','085233445566','fajar.n@email.com'),(10,'Indah Permata','Jl. Sunset Road No. 88, Bali','081911223344','indah.p@email.com'),(11,'Aditya Pratama','Jl. Pemuda No. 19, Semarang','081344556677','aditya.p@email.com'),(12,'Nurul Hidayah','Jl. Margonda Raya No. 50, Depok','085788990011','nurul.h@email.com');
/*!40000 ALTER TABLE `tamu` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-23  0:12:25
