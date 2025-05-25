-- Table structure for table `admin`
CREATE TABLE `admin` (
  `admin_id` int NOT NULL,
  `password` char(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `department`
CREATE TABLE `department` (
  `department_code` varchar(10) NOT NULL,
  `department_name` varchar(50) DEFAULT NULL,
  `dean_name` varchar(50) DEFAULT NULL,
  `dean_email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`department_code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `lecturer`
CREATE TABLE `lecturer` (
  `lecturer_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` char(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `level` varchar(5) DEFAULT NULL,
  `department_code` varchar(10) DEFAULT NULL,
  `ic_no` varchar(12) NOT NULL,
  PRIMARY KEY (`lecturer_id`),
  UNIQUE KEY `ic_no` (`ic_no`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `lecturer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `lecturer_files`
CREATE TABLE `lecturer_file` (
  `file_id` INT NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `lecturer_id` int NOT NULL,
  `lecturer_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`file_id`),
  KEY `lecturer_id` (`lecturer_id`),
  CONSTRAINT `lecturer_file_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `program_officer`
CREATE TABLE `program_officer` (
  `po_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` char(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `department_code` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`po_id`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `program_officer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `other`
CREATE TABLE `other` (
  `other_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`other_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Table structure for table `hop`
/* CREATE TABLE `hop` (
  `hop_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `department_code` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`hop_id`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `hop_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE CASCADE,
) ENGINE=InnoDB DEFAULT CHARSET=latin1; */

-- Table structure for table `subject`
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

-- Table structure for table `subject_levels`
CREATE TABLE `subject_levels` (
  `subject_code` varchar(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `level` varchar(50) NOT NULL,
  PRIMARY KEY (`subject_code`,`level`),
  CONSTRAINT `subject_levels_ibfk_1` FOREIGN KEY (`subject_code`) REFERENCES `subject` (`subject_code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `hop` (
  `hop_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `level` varchar(50) NOT NULL,
  `department_code` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`hop_id`),
  CONSTRAINT `hop_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `approval` (
  `approval_id` int NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `last_updated` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`approval_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
