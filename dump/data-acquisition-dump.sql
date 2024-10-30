-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: coursepdfextractor
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `admin_id` int NOT NULL,
  `password` char(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'$2b$12$O76VsEWxQoE8y/j.il/1C.jEUMrEPr5iUI91Pfoj3ikkUxCeJoAge','admin1@example.com');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `department_code` varchar(10) NOT NULL,
  `department_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`department_code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES ('BIZ','Business'),('CS','Computer Sciences'),('ENG','Engineering'),('MATH','Mathematics');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;

--
-- Table structure for table `lecturer`
--

DROP TABLE IF EXISTS `lecturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecturer` (
  `lecturer_id` int NOT NULL AUTO_INCREMENT,
  `lecturer_name` varchar(50) DEFAULT NULL,
  `email_address` varchar(100) DEFAULT NULL,
  `level` varchar(5) DEFAULT NULL,
  `department_code` varchar(10) DEFAULT NULL,
  `ic_no` varchar(12) NOT NULL,
  PRIMARY KEY (`lecturer_id`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `lecturer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecturer`
--

/*!40000 ALTER TABLE `lecturer` DISABLE KEYS */;
INSERT INTO `lecturer` VALUES (1,'Dr. John Smith','jsmith@university.edu','3','CS','123456789012'),(2,'Prof. Jane Doe','jdoe@university.edu','4','ENG','210987654321'),(3,'Mr. Alan Turing','aturing@university.edu','2','ENG','123423455678'),(4,'Ms. Ada Lovelace','alovelace@university.edu','3','MATH','326534323654'),(8,'test','test@test.com','III','CS','123456123456');
/*!40000 ALTER TABLE `lecturer` ENABLE KEYS */;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `password` char(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `department_code` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `department_id` (`department_code`),
  CONSTRAINT `person_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'$2b$12$TyShgHm6Z8Pn2/DBroysV.iZiRGD8avC5HgZMYfB.jGBiba57Yrzq','johndoe@example.com','CS'),(2,'$2b$12$fqUJc99wmQXzagQd2kc3ouYlggXVZsLbbC6Uuw57GvGInpYcl4dti','janedoe@example.com','ENG'),(3,'$2b$12$dU1m7ASURcU2wH8IxPsF6.NiAagR8f2WIHDb6JchWs0Lp2NW8s/A6','alicew@example.com','MATH'),(4,'$2b$12$vTtlbUg9L3oEh20GThwmXeSQvpb6uOpKH4JklL71lcFifZ8rWd8CO','bobsmith@example.com','CS');
/*!40000 ALTER TABLE `person` ENABLE KEYS */;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `subject_code` varchar(10) NOT NULL,
  `subject_title` varchar(100) DEFAULT NULL,
  `program_code` varchar(10) DEFAULT NULL,
  `lecture_hours` int DEFAULT '0',
  `tutorial_hours` int DEFAULT '0',
  `practical_hours` int DEFAULT '0',
  `blended_hours` int DEFAULT '0',
  `lecture_weeks` int DEFAULT '0',
  `tutorial_weeks` int DEFAULT '0',
  `practical_weeks` int DEFAULT '0',
  `blended_weeks` int DEFAULT '0',
  `subject_level` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`subject_code`),
  KEY `program_code` (`program_code`),
  CONSTRAINT `subject_ibfk_3` FOREIGN KEY (`program_code`) REFERENCES `program` (`program_code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject`
--

/*!40000 ALTER TABLE `subject` DISABLE KEYS */;
INSERT INTO `subject` VALUES ('CAP2000','test',NULL,2,0,2,1,14,0,13,14,'Diploma'),('CAP2100','Capstone Project',NULL,0,0,0,0,0,0,0,14,'Diploma'),('COM2111','Writing Skills',NULL,2,1,0,1,14,14,0,14,'Diploma'),('DCS1101','Programming Fundamentals',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS1102','Computer Architecture',NULL,2,0,2,1,14,0,7,14,'Diploma'),('DCS1103','User Experience (UX) Design',NULL,2,1,0,1,14,14,0,14,'Diploma'),('DCS1104','Introduction to Statistics and Data Analytics',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS1105','Business Innovation in Industry 4.0',NULL,2,1,0,1,14,14,0,14,'Diploma'),('DCS1106','Operating Systems',NULL,2,0,2,1,14,0,7,14,'Diploma'),('DCS2101','Data Structures',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2102','Rapid Application Development',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2103','High Level Programming',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2104','Data Visualization',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2105','Business Intelligence',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2106','Data Mining',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2107','Cloud Computing Fundamentals',NULL,2,1,2,1,14,14,7,14,'Diploma'),('DCS2108','Cloud Computing Architecture',NULL,2,1,2,1,14,14,7,14,'Diploma'),('DCS2109','Cloud Implementation and Deployment',NULL,2,0,2,1,14,0,13,14,'Diploma'),('DCS2110','Cybersecurity Fundamentals',NULL,2,1,0,1,14,14,0,14,'Diploma'),('DCS2112','Digital Forensics',NULL,2,0,2,1,14,0,7,14,'Diploma'),('DCS2113','Digital and Cyber Laws',NULL,2,1,0,1,14,14,0,14,'Diploma'),('DUM1001','Dummy Module',NULL,0,0,0,0,0,0,0,14,'Diploma'),('DUM1002','Dummy Module',NULL,0,0,0,0,0,0,0,14,'Diploma'),('DUM2001','Dummy Module',NULL,0,0,0,0,0,0,0,14,'Diploma'),('DUM2002','Dummy Module',NULL,0,0,0,0,0,0,0,14,'Diploma'),('IBM1101','Introduction to IT Infrastructure Landscape',NULL,2,0,0,1,14,0,0,14,'Diploma'),('IBM2101','Introduction to Business Analytics',NULL,2,1,0,1,14,14,0,14,'Diploma'),('IBM2102','Introduction to Cloud Computing',NULL,2,0,2,1,14,0,7,14,'Diploma'),('IBM2104','Introduction to Web Programming with PHP',NULL,2,0,2,1,14,0,13,14,'Diploma'),('IBM2105','Introduction to Mobile Apps Development',NULL,2,0,2,1,14,0,13,14,'Diploma'),('IBM2107','Information Technology Infrastructure Library',NULL,2,1,0,1,14,14,0,14,'Diploma'),('IBM2108','IT Service Management',NULL,2,1,0,1,14,14,0,14,'Diploma'),('ICT1101','Program Logic Formulation',NULL,2,0,2,1,14,0,7,14,'Diploma'),('ICT1102','Introduction to Internet Technologies',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT1103','Structured Programming',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT1104','Database Management',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT1105','Fundamentals of Networking',NULL,2,0,2,1,14,0,7,14,'Diploma'),('ICT1106','System Analysis and Design',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT1110','Introduction to Human Computer Interaction',NULL,2,1,0,1,14,14,0,14,'Diploma'),('ICT2101','Computer Organization',NULL,2,0,2,1,14,0,7,14,'Diploma'),('ICT2102','Introduction to Data Structure',NULL,2,0,0,1,14,0,0,14,'Diploma'),('ICT2104','Computer Ethics',NULL,2,1,0,1,14,14,0,14,'Diploma'),('ICT2106','Fundamentals of Trustworthy Computing',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT2108','Digital Image Editing',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT2113','Object Oriented Programming',NULL,2,0,2,1,14,0,13,14,'Diploma'),('ICT2114','Computer Ethics',NULL,2,1,0,1,14,14,0,14,'Diploma'),('INT2100','Internship',NULL,0,0,0,0,0,0,0,14,'Diploma'),('MAT1103','Fundamentals of Mathematics',NULL,1,1,0,1,14,14,0,14,'Diploma'),('MAT1104','Discrete Mathematics',NULL,1,1,0,1,14,14,0,14,'Diploma'),('MGT1103','Fundamentals of Management',NULL,1,1,0,1,14,14,0,14,'Diploma'),('MPU2133','BM Komunikasi 1B',NULL,2,0,0,1,3,0,0,14,'Diploma'),('MPU2163','Pengajian Malaysia 2',NULL,2,0,0,1,3,0,0,14,'Diploma'),('MPU2183','Penghayatan Etika & Peradaban',NULL,2,0,0,1,3,0,0,14,'Diploma'),('MPU2213','Bahasa Kebangsaan A*',NULL,2,0,0,1,3,0,0,14,'Diploma'),('MPU2242','Media Literacy for Personal Branding',NULL,1,0,0,1,3,0,0,14,'Diploma'),('MPU2332','Green Future Malaysia',NULL,1,0,0,1,3,0,0,14,'Diploma'),('MPU2342','Integrity and Anti-Corruption (KIAR)',NULL,2,0,0,1,3,0,0,14,'Diploma'),('MPU2432','Co-curriculum',NULL,1,0,0,1,3,0,0,14,'Diploma'),('STA1106','Quantitative Methods',NULL,2,1,2,1,14,14,13,14,'Diploma');
/*!40000 ALTER TABLE `subject` ENABLE KEYS */;

--
-- Dumping routines for database 'coursepdfextractor'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-30 22:10:55
