@IsTest
private class SmokeTestPingResourceTest {

    @IsTest
    static void pingReturnsOk() {
        // Optional REST context setup (doGet doesn't read it, but mirrors real call shape)
        RestRequest req = new RestRequest();
        RestResponse res = new RestResponse();
        req.httpMethod = 'GET';
        req.requestUri = '/services/apexrest/smoketest/v1/ping';
        RestContext.request = req;
        RestContext.response = res;

        Test.startTest();
        SmokeTestPingResource.PingResponse out = SmokeTestPingResource.doGet();
        Test.stopTest();

        System.assertNotEquals(null, out, 'Response should not be null');
        System.assertEquals('OK', out.status, 'Status should be OK');
        System.assertEquals(UserInfo.getOrganizationId(), out.orgId, 'OrgId should match');
        System.assertEquals(UserInfo.getUserId(), out.userId, 'UserId should match');
        System.assertEquals('Smoke test endpoint reachable.', out.message, 'Message should match');

        System.assertNotEquals(null, out.timestampUtc, 'timestampUtc should not be null');
        System.assert(out.timestampUtc.contains('T'), 'timestampUtc should be ISO-like');
        System.assert(out.timestampUtc.endsWith('Z'), 'timestampUtc should be GMT Zulu');

        // Basic format check: yyyy-MM-ddTHH:mm:ssZ
        System.assertEquals(20, out.timestampUtc.length(), 'Unexpected timestamp length');
        System.assertEquals('-', out.timestampUtc.substring(4, 5));
        System.assertEquals('-', out.timestampUtc.substring(7, 8));
        System.assertEquals('T', out.timestampUtc.substring(10, 11));
        System.assertEquals(':', out.timestampUtc.substring(13, 14));
        System.assertEquals(':', out.timestampUtc.substring(16, 17));
        System.assertEquals('Z', out.timestampUtc.substring(19, 20));
    }
}
