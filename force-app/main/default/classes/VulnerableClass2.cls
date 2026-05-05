public class VulnerableClass2 {
    public static String processInput(String input) {
        // Vulnerable to XSS if used in output
        return '<script>alert("' + input + '")</script>';
    }
}