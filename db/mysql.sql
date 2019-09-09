use movie;
create table if not exists `Movies` (
	`id` int unsigned auto_increment,
	`ChineseName` varchar(100) not null default '',
	`OtherName` varchar(100) not null default '',
	`area` varchar(100) not null default '',
	`ReleaseTime` date not null default '1000-01-01',
	primary key (`id`),
	unique key `MovieInfos`(`ChineseName`,`OtherName`,`area`,`ReleaseTime`),
	key (`ChineseName`),
	key (`OtherName`),
	key `area` (`area`)
)engine=InnoDB auto_increment=0 default charset=utf8;

create table if not exists `Magnets`(
	`id` int unsigned auto_increment,
	`magnetURL` varchar(300) not null default '',
	`movieId` int unsigned not null,
	primary key (`id`),
	foreign key (`movieId`) references Movies(`id`)
)engine=InnoDB auto_increment=0 default charset=utf8;

create table if not exists `Directors`(
	`id` int unsigned auto_increment,
	`director` varchar(100) not null,
	`movieId` int unsigned not null,
	primary key (`id`),
	key `director` (`director`),
	foreign key (`movieId`) references Movies(`id`)
)engine=InnoDB auto_increment=0 default charset=utf8;

create table if not exists `Actors`(
	`id` int unsigned auto_increment,
	`actor` varchar(100) not null,
	`movieId` int unsigned not null,
	primary key (`id`),
	key `actor` (`actor`),
	foreign key (`movieId`) references Movies(`id`)
)engine=InnoDB auto_increment=0 default charset=utf8;

create table if not exists `Types`(
	`id` int unsigned auto_increment,
	`type` varchar(100) not null,
	`movieId` int unsigned not null,
	primary key (`id`),
	key `type` (`type`),
	foreign key (`movieId`) references Movies(`id`)
)engine=InnoDB auto_increment=0 default charset=utf8;
