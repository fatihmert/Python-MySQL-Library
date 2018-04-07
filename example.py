
pymysql = MySQL("localhost","fmdogancan","root","")

# Get all
pymysql.all("SELECT * FROM users")

# Row counts
pymysql.count 

# Get all with Where
pymysql.all("SELECT * FROM users WHERE role = %s AND group_ = %s",('admin',5))

# Get first row
pymysql.firstRow("SELECT * FROM users")

# Insert one data
one_data = {
	# Column : Value
	'name' : 'Fatih',
	'role' : 'admin',
	'group_' : 5,
	'psw' : "123"
}

pymysql.insert('users',one_data)

# Multiple insert data
# Should be same columns each data
mult_data = [
	{
		'name' : 'Ömer',
		'role' : 'admin',
		'group_' : 3,
		'psw' : "321"
	},
	{
		'name' : 'Fatih',
		'role' : 'admin',
		'group_' : 5,
		'psw' : "123"
	}
]

pymysql.insert('users',mult_data)

# Delete all
pymysql.delete('users')

# Delete with Where
where_cond = "group_=3 AND role='standard'"
pymysql.delete('users',where_cond)

# All update
pymysql.update('users',one_data)

# Update with Where
pymysql.update('users',one_data,where_cond)

# Create table
groups_table = {
	'id' : pymysql.col.increment(),
	'name' : pymysql.col.varchar(30),
}
pymysql.create('groups',groups_table,True)

# Get column list
pymysql.columnList('users')

# Get table list
pymysql.tableList()

# Change db
pymysql.usedb('other_db')

# Get Config Details
pymysql.getConfig()

# Raw Query
pymysql.rawQuery("ALTER TABLE users ADD ip_addr varchar(30)")

# Table Exist
pymysql.tableExist('posts')

# DB Exist
pymysql.dbExist('other_db')


