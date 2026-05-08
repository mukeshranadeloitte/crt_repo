public class VulnerableClass1 {
    public static List<Account> getAccounts(String name) {
        // Vulnerable to SQL Injection
        String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + name + '\'';
        return Database.query(query);
    }
}