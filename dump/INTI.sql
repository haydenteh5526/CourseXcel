CREATE TABLE `admin` (
  `admin_id` INT NOT NULL AUTO_INCREMENT,
  `password` CHAR(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `department` (
  `department_id` INT NOT NULL AUTO_INCREMENT,
  `department_code` VARCHAR(10) NOT NULL,
  `department_name` VARCHAR(50) DEFAULT NULL,
  `dean_name` VARCHAR(50) DEFAULT NULL,
  `dean_email` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`department_id`),
  UNIQUE KEY `department_code` (`department_code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `subject` (
  `subject_id` INT NOT NULL AUTO_INCREMENT,
  `subject_code` VARCHAR(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `subject_title` VARCHAR(100) DEFAULT NULL,
  `subject_level` VARCHAR(50) DEFAULT NULL,
  `lecture_hours` INT DEFAULT '0',
  `tutorial_hours` INT DEFAULT '0',
  `practical_hours` INT DEFAULT '0',
  `blended_hours` INT DEFAULT '0',
  `lecture_weeks` INT DEFAULT '0',
  `tutorial_weeks` INT DEFAULT '0',
  `practical_weeks` INT DEFAULT '0',
  `blended_weeks` INT DEFAULT '0',
  `head_id` INT DEFAULT NULL, 
  PRIMARY KEY (`subject_id`),
  UNIQUE KEY `subject_code` (`subject_code`),
  KEY `head_id` (`head_id`),
  CONSTRAINT `subject_ibfk_1` FOREIGN KEY (`head_id`) REFERENCES `head` (`head_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `program_officer` (
  `po_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` CHAR(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `department_code` VARCHAR(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`po_id`),
  KEY `department_code` (`department_code`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `program_officer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer` (
  `lecturer_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` CHAR(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `level` VARCHAR(5) DEFAULT NULL,
  `department_code` VARCHAR(10) DEFAULT NULL,
  `ic_no` VARCHAR(12) NOT NULL,
  PRIMARY KEY (`lecturer_id`),
  UNIQUE KEY `ic_no` (`ic_no`),
  UNIQUE KEY `email` (`email`),
  KEY `department_code` (`department_code`),
  CONSTRAINT `lecturer_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer_file` (
  `file_id` INT NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `lecturer_id` INT NOT NULL,
  `lecturer_name` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`file_id`),
  KEY `lecturer_id` (`lecturer_id`),
  CONSTRAINT `lecturer_file_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `head` (
  `head_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `level` VARCHAR(50) NOT NULL,
  `department_code` VARCHAR(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`head_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `head_ibfk_1` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `other` (
  `other_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `role` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`other_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `requisition_approval` (
  `approval_id` INT NOT NULL AUTO_INCREMENT,
  `department_code` VARCHAR(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `lecturer_name` VARCHAR(50) DEFAULT NULL,
  `subject_level` VARCHAR(50) DEFAULT NULL,
  `sign_col` INT DEFAULT NULL,
  `po_email` VARCHAR(100) DEFAULT NULL,
  `head_email` VARCHAR(100) DEFAULT NULL,
  `dean_email` VARCHAR(100) DEFAULT NULL,
  `ad_email` VARCHAR(100) DEFAULT NULL,
  `hr_email` VARCHAR(100) DEFAULT NULL,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT NULL,
  `last_updated` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`approval_id`),
  KEY `po_email` (`po_email`),
  CONSTRAINT `requisition_approval_ibfk_1` FOREIGN KEY (`po_email`) REFERENCES `program_officer` (`email`) ON DELETE SET NULL,
  CONSTRAINT `requisition_approval_ibfk_2` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer_subject` (
  `subject_id` INT NOT NULL AUTO_INCREMENT,
  `subject_level` VARCHAR(50) DEFAULT NULL,
  `subject_code` VARCHAR(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `subject_title` VARCHAR(100) DEFAULT NULL, 
  `start_date` DATE DEFAULT NULL,
  `end_date` DATE DEFAULT NULL,
  `total_lecture_hours` INT DEFAULT 0,
  `total_tutorial_hours` INT DEFAULT 0,
  `total_practical_hours` INT DEFAULT 0,
  `total_blended_hours` INT DEFAULT 0,
  `hourly_rate` INT DEFAULT '0',
  `total_cost` DECIMAL(9,4) DEFAULT '0.0000',
  `lecturer_id` INT NOT NULL,
  `requisition_id` INT NOT NULL,
  PRIMARY KEY (`subject_id`),
  UNIQUE KEY `subject_code` (`subject_code`),
  KEY `lecturer_id` (`lecturer_id`),
  KEY `requisition_id` (`requisition_id`),
  CONSTRAINT `lecturer_subject_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_subject_ibfk_2` FOREIGN KEY (`requisition_id`) REFERENCES `requisition_approval` (`approval_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `claim_approval` (
  `approval_id` INT NOT NULL AUTO_INCREMENT,
  `lecturer_name` VARCHAR(50) DEFAULT NULL,
  `department_code` VARCHAR(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `sign_col` INT DEFAULT NULL,
  `lecturer_email` VARCHAR(100) DEFAULT NULL,
  `po_email` VARCHAR(100) DEFAULT NULL,
  `head_email` VARCHAR(100) DEFAULT NULL,
  `dean_email` VARCHAR(100) DEFAULT NULL,
  `ad_email` VARCHAR(100) DEFAULT NULL,
  `hr_email` VARCHAR(100) DEFAULT NULL,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT NULL,
  `last_updated` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`approval_id`),
  KEY `lecturer_email` (`lecturer_email`),
  CONSTRAINT `claim_approval_ibfk_1` FOREIGN KEY (`lecturer_email`) REFERENCES `lecturer` (`email`) ON DELETE SET NULL,
  CONSTRAINT `claim_approval_ibfk_2` FOREIGN KEY (`department_code`) REFERENCES `department` (`department_code`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;