@IsTest
private class CoverageDemoServiceTest {
    @IsTest
    static void minimalCoverage_below70() {
        // Only covers one tier branch + clamp return path
        Integer d = CoverageDemoService.calcDiscount(1000, 'SILVER');
        System.assertEquals(70, d, '7% of 1000 should be 70');

        // Covers only the early-null return path in computeRiskScore
        System.assertEquals(0, CoverageDemoService.computeRiskScore(null));
    }
}
