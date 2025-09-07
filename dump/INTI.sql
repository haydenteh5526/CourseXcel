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
  -- UNIQUE KEY `subject_code` (`subject_code`),
  KEY `head_id` (`head_id`),
  CONSTRAINT `subject_ibfk_1` FOREIGN KEY (`head_id`) REFERENCES `head` (`head_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `head` (
  `head_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `level` VARCHAR(50) NOT NULL,
  `department_id` INT DEFAULT NULL,
  PRIMARY KEY (`head_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `head_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `program_officer` (
  `po_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` CHAR(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `department_id` INT DEFAULT NULL,
  PRIMARY KEY (`po_id`),
  KEY `department_id` (`department_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `program_officer_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer` (
  `lecturer_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` CHAR(76) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `level` VARCHAR(5) DEFAULT NULL,
  `department_id` INT DEFAULT NULL,
  `ic_no` LONGBLOB NOT NULL,
  PRIMARY KEY (`lecturer_id`),
  UNIQUE KEY `ic_no` (`ic_no`(16));
  UNIQUE KEY `email` (`email`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `lecturer_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `other` (
  `other_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `role` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`other_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `rate` (
  `rate_id` INT NOT NULL AUTO_INCREMENT,
  `amount` INT DEFAULT '0',
  `status` BOOLEAN DEFAULT NULL,
  PRIMARY KEY (`rate_id`),
  UNIQUE KEY `amount` (`amount`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `requisition_approval` (
  `approval_id` INT NOT NULL AUTO_INCREMENT,
  `department_id` INT DEFAULT NULL,
  `lecturer_id` INT DEFAULT NULL,
  `po_id` INT DEFAULT NULL,
  `head_id` INT DEFAULT NULL,
  `subject_level` VARCHAR(50) DEFAULT NULL,
  `sign_col` INT DEFAULT NULL,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT NULL,
  `last_updated` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`approval_id`),
  KEY `department_id` (`department_id`),
  KEY `lecturer_id` (`lecturer_id`),
  KEY `po_id` (`po_id`),
  KEY `head_id` (`head_id`),
  CONSTRAINT `requisition_approval_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`) ON DELETE SET NULL,
  CONSTRAINT `requisition_approval_ibfk_2` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE SET NULL,
  CONSTRAINT `requisition_approval_ibfk_3` FOREIGN KEY (`po_id`) REFERENCES `program_officer` (`po_id`) ON DELETE SET NULL,
  CONSTRAINT `requisition_approval_ibfk_4` FOREIGN KEY (`head_id`) REFERENCES `head` (`head_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer_subject` (
  `lecturer_id` INT NOT NULL,
  `requisition_id` INT NOT NULL,
  `subject_id` INT DEFAULT NULL,
  `start_date` DATE DEFAULT NULL,
  `end_date` DATE DEFAULT NULL,
  `total_lecture_hours` INT DEFAULT 0,
  `total_tutorial_hours` INT DEFAULT 0,
  `total_practical_hours` INT DEFAULT 0,
  `total_blended_hours` INT DEFAULT 0,
  `rate_id` INT DEFAULT NULL,
  `total_cost` INT DEFAULT NULL,
  KEY `lecturer_id` (`lecturer_id`),
  KEY `requisition_id` (`requisition_id`),
  KEY `subject_id` (`subject_id`),
  KEY `rate_id` (`rate_id`),
  CONSTRAINT `lecturer_subject_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_subject_ibfk_2` FOREIGN KEY (`requisition_id`) REFERENCES `requisition_approval` (`approval_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_subject_ibfk_3` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) ON DELETE SET NULL,
  CONSTRAINT `lecturer_subject_ibfk_4` FOREIGN KEY (`rate_id`) REFERENCES `rate` (`rate_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `requisition_attachment` (
  `attachment_id` INT NOT NULL AUTO_INCREMENT,
  `attachment_name` VARCHAR(100) DEFAULT NULL,
  `attachment_url` VARCHAR(500) DEFAULT NULL,
  `lecturer_id` INT NOT NULL,
  `requisition_id` INT NOT NULL,
  PRIMARY KEY (`attachment_id`),
  KEY `lecturer_id` (`lecturer_id`),
  KEY `requisition_id` (`requisition_id`),
  CONSTRAINT `requisition_attachment_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE,
  CONSTRAINT `requisition_attachment_ibfk_2` FOREIGN KEY (`requisition_id`) REFERENCES `requisition_approval` (`approval_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `claim_approval` (
  `approval_id` INT NOT NULL AUTO_INCREMENT,
  `department_id` INT DEFAULT NULL,
  `lecturer_id` INT DEFAULT NULL,
  `po_id` INT DEFAULT NULL,
  `head_id` INT DEFAULT NULL,
  `subject_level` VARCHAR(50) DEFAULT NULL,
  `sign_col` INT DEFAULT NULL,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT NULL,
  `last_updated` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`approval_id`),
  KEY `department_id` (`department_id`),
  KEY `lecturer_id` (`lecturer_id`),
  CONSTRAINT `claim_approval_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`) ON DELETE SET NULL,
  CONSTRAINT `claim_approval_ibfk_2` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE SET NULL,
  CONSTRAINT `claim_approval_ibfk_3` FOREIGN KEY (`po_id`) REFERENCES `program_officer` (`po_id`) ON DELETE SET NULL,
  CONSTRAINT `claim_approval_ibfk_4` FOREIGN KEY (`head_id`) REFERENCES `head` (`head_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lecturer_claim` (
  `lecturer_id` INT NOT NULL,
  `requisition_id` INT NOT NULL,
  `claim_id` INT NOT NULL,
  `subject_id` INT DEFAULT NULL,
  `date` DATE DEFAULT NULL,
  `lecture_hours` INT DEFAULT 0,
  `tutorial_hours` INT DEFAULT 0,
  `practical_hours` INT DEFAULT 0,
  `blended_hours` INT DEFAULT 0,
  `rate_id` INT DEFAULT NULL,
  `total_cost` INT DEFAULT NULL,
  KEY `lecturer_id` (`lecturer_id`),
  KEY `requisition_id` (`requisition_id`),
  KEY `claim_id` (`claim_id`),
  KEY `subject_id` (`subject_id`),
  KEY `rate_id` (`rate_id`),
  CONSTRAINT `lecturer_claim_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_claim_ibfk_2` FOREIGN KEY (`requisition_id`) REFERENCES `requisition_approval` (`approval_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_claim_ibfk_3` FOREIGN KEY (`claim_id`) REFERENCES `claim_approval` (`approval_id`) ON DELETE CASCADE,
  CONSTRAINT `lecturer_claim_ibfk_4` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) ON DELETE SET NULL,
  CONSTRAINT `lecturer_claim_ibfk_5` FOREIGN KEY (`rate_id`) REFERENCES `rate` (`rate_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `claim_attachment` (
  `attachment_id` INT NOT NULL AUTO_INCREMENT,
  `attachment_name` VARCHAR(100) DEFAULT NULL,
  `attachment_url` VARCHAR(500) DEFAULT NULL,
  `lecturer_id` INT NOT NULL,
  `claim_id` INT NOT NULL,
  PRIMARY KEY (`attachment_id`),
  KEY `lecturer_id` (`lecturer_id`),
  KEY `claim_id` (`claim_id`),
  CONSTRAINT `claim_attachment_ibfk_1` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`) ON DELETE CASCADE,
  CONSTRAINT `claim_attachment_ibfk_2` FOREIGN KEY (`claim_id`) REFERENCES `claim_approval` (`approval_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `requisition_report` (
  `report_id` INT NOT NULL AUTO_INCREMENT,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `start_date` DATE DEFAULT NULL,
  `end_date` DATE DEFAULT NULL,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `claim_report` (
  `report_id` INT NOT NULL AUTO_INCREMENT,
  `file_id` VARCHAR(100) DEFAULT NULL,
  `file_name` VARCHAR(100) DEFAULT NULL,
  `file_url` VARCHAR(500) DEFAULT NULL,
  `start_date` DATE DEFAULT NULL,
  `end_date` DATE DEFAULT NULL,
  PRIMARY KEY (`report_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;