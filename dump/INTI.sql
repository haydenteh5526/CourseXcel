-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: coursepdfextractor
-- ------------------------------------------------------
-- Server version	8.0.39

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

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'$2b$12$O76VsEWxQoE8y/j.il/1C.jEUMrEPr5iUI91Pfoj3ikkUxCeJoAge','admin1@example.com');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES ('BIZ','Business'),('CS','Computer Sciences'),('ENG','Engineering'),('MATH','Mathematics');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecturer`
--

DROP TABLE IF EXISTS `lecturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecturer` (
  `lecturer_id` int NOT NULL AUTO_INCREMENT,
  `lecturer_name` varchar(50) DEFAULT NULL,
  `level` varchar(5) DEFAULT NULL,
  `department_code` varchar(10) DEFAULT NULL,
  `ic_no` varchar(12) NOT NULL,
  PRIMARY KEY (`lecturer_id`),
  UNIQUE KEY `ic_no` (`ic_no`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `lecturer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecturer`
--

LOCK TABLES `lecturer` WRITE;
/*!40000 ALTER TABLE `lecturer` DISABLE KEYS */;
INSERT INTO `lecturer` VALUES (1,'Dr. John Smith','3','CS','123456789012'),(2,'Prof. Jane Doe','4','ENG','210987654321'),(3,'Mr. Alan Turing','2','ENG','123423455678'),(4,'Ms. Ada Lovelace','3','MATH','326534323654'),(13,'Hayden','III','CS','123412341234'),(16,'Hayden Teh','III','ENG','123451234512');
/*!40000 ALTER TABLE `lecturer` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'$2b$12$1Kc4nAVNbPc4YAkGqIg9H.ix2qDoFblaqLnRQOdckcetdMJzQxdCe','johndoe@example.com','CS'),(2,'$2b$12$fqUJc99wmQXzagQd2kc3ouYlggXVZsLbbC6Uuw57GvGInpYcl4dti','janedoe@example.com','ENG'),(3,'$2b$12$dU1m7ASURcU2wH8IxPsF6.NiAagR8f2WIHDb6JchWs0Lp2NW8s/A6','alicew@example.com','MATH'),(4,'$2b$12$vTtlbUg9L3oEh20GThwmXeSQvpb6uOpKH4JklL71lcFifZ8rWd8CO','bobsmith@example.com','CS');
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `subject_code` varchar(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `subject_title` varchar(100) DEFAULT NULL,
  `lecture_hours` int DEFAULT '0',
  `tutorial_hours` int DEFAULT '0',
  `practical_hours` int DEFAULT '0',
  `blended_hours` int DEFAULT '0',
  `lecture_weeks` int DEFAULT '0',
  `tutorial_weeks` int DEFAULT '0',
  `practical_weeks` int DEFAULT '0',
  `blended_weeks` int DEFAULT '0',
  PRIMARY KEY (`subject_code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
/*!40000 ALTER TABLE `subject` DISABLE KEYS */;
INSERT INTO `subject` VALUES ('CAP2100','Capstone Project',0,0,0,0,0,0,0,14),('CIT 1000','INTRODUCTION TO INFORMATION TECHNOLOGY',2,0,2,1,14,0,13,14),('CIT1001','INTRODUCTION TO COMPUTER ARCHITECTURE AND ORGANIZATION',2,2,0,1,14,13,0,14),('CIT1002','INTRODUCTION TO PC MAINTENANCE AND SUPPORT',2,0,2,1,14,0,13,14),('CIT1003','FUNDAMENTALS OF PROGRAMMING',2,0,2,1,14,0,13,14),('CIT1004','INTRODUCTION TO DATABASE',2,0,2,1,14,0,13,14),('CIT1005','INTRODUCTION TO NETWORKING',2,0,2,1,14,0,13,14),('CIT1006','INTERNET TECHNOLOGY AND APPLCICATIONS',2,0,2,1,14,0,13,14),('CIT1007','INTRODUCTION TO OPERATING SYSTEMS',2,2,0,1,14,14,0,14),('CIT1008','INTRODUCTION TO VISUAL PROGRAMMING',2,1,2,1,14,8,9,14),('CIT1009','INTRODUCTION TO JAVA PROGRAMMING',2,0,2,1,14,0,13,14),('CIT1011','FUNDAMENTALS OF PROGRAMMING',2,0,2,1,14,0,13,14),('CIT1012','INTRODUCTION TO JAVA PROGRAMMING',2,2,0,1,14,13,0,14),('COM1003','BUSINESS COMMUNICATION SKILLS',2,1,0,1,14,14,0,14),('COM2111','Writing Skills',2,1,0,1,14,14,0,14),('CSC 1215','BASIC COMPUTING',2,0,2,1,14,0,14,14),('CSC1211','PROGRAMMING TECHNIQUE',2,0,2,1,14,0,14,14),('CSC1212','DATA COMMUNICATIONS AND NETWORKING',2,1,0,1,14,14,0,14),('CSC1213','INTRODUCTION TO DATABASE MANAGEMENT SYSTEM',2,0,2,1,14,0,14,14),('DCS1101','Programming Fundamentals',2,0,2,1,14,0,13,14),('DCS1102','Computer Architecture',2,0,2,1,14,0,7,14),('DCS1103','User Experience (UX) Design',2,1,0,1,14,14,0,14),('DCS1104','Introduction to Statistics and Data Analytics',2,0,2,1,14,0,13,14),('DCS1105','Business Innovation in Industry 4.0',2,1,0,1,14,14,0,14),('DCS1106','Operating Systems',2,0,2,1,14,0,7,14),('DCS2101','Data Structures',2,0,2,1,14,0,13,14),('DCS2102','Rapid Application Development',2,0,2,1,14,0,13,14),('DCS2103','High Level Programming',2,0,2,1,14,0,13,14),('DCS2104','Data Visualization',2,0,2,1,14,0,13,14),('DCS2105','Business Intelligence',2,0,2,1,14,0,13,14),('DCS2106','Data Mining',2,0,2,1,14,0,13,14),('DCS2107','Cloud Computing Fundamentals',2,1,2,1,14,14,7,14),('DCS2108','Cloud Computing Architecture',2,1,2,1,14,14,7,14),('DCS2109','Cloud Implementation and Deployment',2,0,2,1,14,0,13,14),('DCS2110','Cybersecurity Fundamentals',2,1,0,1,14,14,0,14),('DCS2112','Digital Forensics',2,0,2,1,14,0,7,14),('DCS2113','Digital and Cyber Laws',2,1,0,1,14,14,0,14),('DUM1001','Dummy Module',0,0,0,0,0,0,0,14),('DUM1002','Dummy Module',0,0,0,0,0,0,0,14),('DUM2001','Dummy Module',0,0,0,0,0,0,0,14),('DUM2002','Dummy Module',0,0,0,0,0,0,0,14),('ENL1200','INTRODUCTORY ENGLISH 1',2,0,0,1,14,0,0,14),('ENL1201','INTRODUCTORY ENGLISH 2',2,1,0,1,14,14,0,14),('ENL1211','ENGLISH LANGUAGE SKILLS 1',2,1,0,1,14,14,0,14),('ENL1212','ENGLISH LANGUAGE SKILLS 2',2,1,0,1,0,14,0,14),('GNS1205','GENERAL STUDIES',2,2,0,1,14,14,0,14),('IBM1101','Introduction to IT Infrastructure Landscape',2,0,0,1,14,0,0,14),('IBM2101','Introduction to Business Analytics',2,1,0,1,14,14,0,14),('IBM2102','Introduction to Cloud Computing',2,0,2,1,14,0,7,14),('IBM2104','Introduction to Web Programming with PHP',2,0,2,1,14,0,13,14),('IBM2105','Introduction to Mobile Apps Development',2,0,2,1,14,0,13,14),('IBM2107','Information Technology Infrastructure Library',2,1,0,1,14,14,0,14),('IBM2108','IT Service Management',2,1,0,1,14,14,0,14),('ICT1101','Program Logic Formulation',2,0,2,1,14,0,7,14),('ICT1102','Introduction to Internet Technologies',2,0,2,1,14,0,13,14),('ICT1103','Structured Programming',2,0,2,1,14,0,13,14),('ICT1104','Database Management',2,0,2,1,14,0,13,14),('ICT1105','Fundamentals of Networking',2,0,2,1,14,0,7,14),('ICT1106','System Analysis and Design',2,0,2,1,14,0,13,14),('ICT1110','Introduction to Human Computer Interaction',2,1,0,1,14,14,0,14),('ICT2101','Computer Organization',2,0,2,1,14,0,7,14),('ICT2102','Introduction to Data Structure',2,0,0,1,14,0,0,14),('ICT2104','Computer Ethics',2,1,0,1,14,14,0,14),('ICT2106','Fundamentals of Trustworthy Computing',2,0,2,1,14,0,13,14),('ICT2108','Digital Image Editing',2,0,2,1,14,0,13,14),('ICT2113','Object Oriented Programming',2,0,2,1,14,0,13,14),('ICT2114','Computer Ethics',2,1,0,1,14,14,0,14),('INT2100','Internship',0,0,0,0,0,0,0,14),('INT4000CEM','Programming and Algorithms',1,0,2,1,14,0,13,14),('INT4003CEM','Object Oriented Programming',1,0,2,1,14,0,13,14),('INT4004CEM','Computer Architecture and Networks',1,0,2,1,14,0,13,14),('INT4005CEM','Database Systems',1,0,1,1,14,0,12,14),('INT4006CEM','Computer Science All 1',1,0,2,1,14,0,13,14),('INT4007CEM','Computer Science All 2',1,0,2,1,14,0,13,14),('INT4008CEM','Computing All 1',1,0,2,1,14,0,13,14),('INT4009CEM','Computing All 2',1,0,2,1,14,0,13,14),('INT4067CEM','Software Design',1,0,2,1,14,0,13,14),('INT4068CEM','Mathematics for Computer Science',2,2,0,1,14,14,0,14),('INT5000CEM','Introduction to Artificial Intelligence',1,0,1,1,14,0,14,14),('INT5001CEM','Software Engineering',2,0,2,1,14,0,13,14),('INT5002CEM','Theory Of Computation',2,2,0,1,14,14,0,14),('INT5003CEM','Advanced Algorithms',2,0,2,1,14,0,13,14),('INT5004CEM','Operating Systems and Security',1,0,3,1,14,0,13,14),('INT5005CEM','Data Science',1,0,1,1,14,0,14,14),('INT5006CEM','People and Computing',1,2,0,1,14,14,0,14),('INT5007CEM','Web Development',1,0,3,1,14,0,14,14),('INT5008CEM','Programming for Developers',1,0,2,1,14,0,13,14),('INT5009CEM','Software Development',2,0,2,1,14,0,13,14),('INT5010CEM','Enterprise Project',1,0,3,1,14,0,13,14),('INT5011CEM','Big Data Programming Project',1,0,2,1,14,0,13,14),('INT5014CEM','Data Science for Developers',1,0,3,1,14,0,13,14),('INT6000CEM','Individual Project Preparation',1,0,0,0,12,0,0,14),('INT6001CEM','Individual Project',1,0,0,0,12,0,0,14),('INT6002CEM','Mobile App Development',1,0,3,1,14,0,13,14),('INT6003CEM','Web API Development',1,0,3,1,14,0,13,14),('INT6004CEM','Parallel Distributed Programming',1,0,3,1,14,0,13,14),('INT6005CEM','Security',2,0,2,1,14,0,13,14),('INT6006CEM','Machine Learning and Related Applications',1,0,3,1,14,0,13,14),('INT6010CEM','Open Source Development',1,0,3,1,14,0,13,14),('INT6012CEM','User Experience Design',1,0,3,1,14,0,13,14),('INTA101SGI','Smart Phone Apps: From Concept to Design and Market',1,2,0,1,14,14,0,14),('INTA202SGI','Android Development Skills',1,0,2,1,14,0,13,14),('INTA301SAM','Events Project Management',1,2,0,1,14,14,0,14),('INTA305IAE','Hi-Tech Entrepreneurship',1,2,0,1,14,14,0,14),('MAT1000','BASIC MATHEMATICS',2,1,0,1,14,14,0,14),('MAT1002','MATHEMATICS FOR COMPUTING',2,1,0,1,14,14,0,14),('MAT1103','Fundamentals of Mathematics',1,1,0,1,14,14,0,14),('MAT1104','Discrete Mathematics',1,1,0,1,14,14,0,14),('MAT1215','FUNDAMENTALS OF MATHEMATICS',2,2,0,1,14,14,0,14),('MAT1217','ADVANCED MATHEMATICS',2,1,0,1,14,14,0,14),('MGT1103','Fundamentals of Management',1,1,0,1,14,14,0,14),('MGT1211','INTRODUCTION TO BUSINESS STUDIES',2,1,0,1,14,14,0,14),('MPU2133','BM Komunikasi 1B',2,0,0,1,3,0,0,14),('MPU2163','Pengajian Malaysia 2',2,0,0,1,3,0,0,14),('MPU2183','Penghayatan Etika & Peradaban',2,0,0,1,3,0,0,14),('MPU2213','Bahasa Kebangsaan A*',2,0,0,1,3,0,0,14),('MPU2242','Media Literacy for Personal Branding',1,0,0,1,3,0,0,14),('MPU2332','Green Future Malaysia',1,0,0,1,3,0,0,14),('MPU2342','Integrity and Anti-Corruption (KIAR)',2,0,0,1,3,0,0,14),('MPU2432','Co-curriculum',1,0,0,1,3,0,0,14),('PDC1107','SELF-DEVELOPMENT SKILLS',2,0,0,1,14,0,0,14),('PDC1109','SKILLS FOR CREATIVE THINKING',2,2,0,1,14,14,0,14),('STA1106','Quantitative Methods',2,1,2,1,14,14,13,14),('STA1203','BUSINESS STATISTICS',2,1,1,1,14,12,14,14);
/*!40000 ALTER TABLE `subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subject_levels`
--

DROP TABLE IF EXISTS `subject_levels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject_levels` (
  `subject_code` varchar(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `level` varchar(50) NOT NULL,
  PRIMARY KEY (`subject_code`,`level`),
  CONSTRAINT `subject_code` FOREIGN KEY (`subject_code`) REFERENCES `subject` (`subject_code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject_levels`
--

LOCK TABLES `subject_levels` WRITE;
/*!40000 ALTER TABLE `subject_levels` DISABLE KEYS */;
INSERT INTO `subject_levels` VALUES ('CAP2100','Diploma'),('CIT 1000','Certificate'),('CIT 1000','Foundation'),('CIT1001','Certificate'),('CIT1002','Certificate'),('CIT1003','Certificate'),('CIT1004','Certificate'),('CIT1005','Certificate'),('CIT1006','Certificate'),('CIT1007','Certificate'),('CIT1008','Certificate'),('CIT1009','Certificate'),('CIT1011','Certificate'),('CIT1012','Certificate'),('COM1003','Certificate'),('COM2111','Diploma'),('CSC 1215','Foundation'),('CSC1211','Foundation'),('CSC1212','Foundation'),('CSC1213','Foundation'),('DCS1101','Diploma'),('DCS1102','Diploma'),('DCS1103','Diploma'),('DCS1104','Diploma'),('DCS1105','Diploma'),('DCS1106','Diploma'),('DCS2101','Diploma'),('DCS2102','Diploma'),('DCS2103','Diploma'),('DCS2104','Diploma'),('DCS2105','Diploma'),('DCS2106','Diploma'),('DCS2107','Diploma'),('DCS2108','Diploma'),('DCS2109','Diploma'),('DCS2110','Diploma'),('DCS2112','Diploma'),('DCS2113','Diploma'),('DUM1001','Diploma'),('DUM1002','Diploma'),('DUM2001','Diploma'),('DUM2002','Diploma'),('ENL1200','Certificate'),('ENL1201','Certificate'),('ENL1211','Foundation'),('ENL1212','Foundation'),('GNS1205','Foundation'),('IBM1101','Diploma'),('IBM2101','Diploma'),('IBM2102','Diploma'),('IBM2104','Diploma'),('IBM2105','Diploma'),('IBM2107','Diploma'),('IBM2108','Diploma'),('ICT1101','Diploma'),('ICT1102','Diploma'),('ICT1103','Diploma'),('ICT1104','Diploma'),('ICT1105','Diploma'),('ICT1106','Diploma'),('ICT1110','Diploma'),('ICT2101','Diploma'),('ICT2102','Diploma'),('ICT2104','Diploma'),('ICT2106','Diploma'),('ICT2108','Diploma'),('ICT2113','Diploma'),('ICT2114','Diploma'),('INT2100','Diploma'),('INT4000CEM','Degree'),('INT4003CEM','Degree'),('INT4004CEM','Degree'),('INT4005CEM','Degree'),('INT4006CEM','Degree'),('INT4007CEM','Degree'),('INT4008CEM','Degree'),('INT4009CEM','Degree'),('INT4067CEM','Degree'),('INT4068CEM','Degree'),('INT5000CEM','Degree'),('INT5001CEM','Degree'),('INT5002CEM','Degree'),('INT5003CEM','Degree'),('INT5004CEM','Degree'),('INT5005CEM','Degree'),('INT5006CEM','Degree'),('INT5007CEM','Degree'),('INT5008CEM','Degree'),('INT5009CEM','Degree'),('INT5010CEM','Degree'),('INT5011CEM','Degree'),('INT5014CEM','Degree'),('INT6000CEM','Degree'),('INT6001CEM','Degree'),('INT6002CEM','Degree'),('INT6003CEM','Degree'),('INT6004CEM','Degree'),('INT6005CEM','Degree'),('INT6006CEM','Degree'),('INT6010CEM','Degree'),('INT6012CEM','Degree'),('INTA101SGI','Degree'),('INTA202SGI','Degree'),('INTA301SAM','Degree'),('INTA305IAE','Degree'),('MAT1000','Certificate'),('MAT1002','Certificate'),('MAT1103','Diploma'),('MAT1104','Diploma'),('MAT1215','Foundation'),('MAT1217','Foundation'),('MGT1103','Diploma'),('MGT1211','Foundation'),('MPU2133','Diploma'),('MPU2163','Diploma'),('MPU2183','Diploma'),('MPU2213','Diploma'),('MPU2242','Diploma'),('MPU2332','Diploma'),('MPU2342','Diploma'),('MPU2432','Diploma'),('PDC1107','Foundation'),('PDC1109','Foundation'),('STA1106','Diploma'),('STA1203','Foundation');
/*!40000 ALTER TABLE `subject_levels` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-01 17:15:36
