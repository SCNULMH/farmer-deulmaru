package com.smhrd.deulmaru.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import org.w3c.dom.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.util.HashMap;
import java.util.Map;

@Service
public class CropScheduleService {

    private static final String BASE_URL = "http://api.nongsaro.go.kr/service/farmWorkingPlanNew/workScheduleEraInfoLst";
    @Value("${nongsaro.api-key:${NONGSARO_API_KEY:}}")
    private String apiKey;
    
 // 작물명과 cntntsNo 매핑 (전체 매핑 값)
    private static final Map<String, String> cropMapping = new HashMap<>();
    static {
        cropMapping.put("가지", "30770");
        cropMapping.put("갓", "30595");
        cropMapping.put("결구상추", "30596");
        cropMapping.put("고들빼기", "30597");
        cropMapping.put("고사리", "30598");
        cropMapping.put("고추(꽈리고추 반촉성)", "30599");
        cropMapping.put("고추(보통재배)", "30600");
        cropMapping.put("고추(촉성재배)", "30601");
        cropMapping.put("곰취", "30602");
        cropMapping.put("근대", "30603");
        cropMapping.put("냉이", "30604");
        cropMapping.put("당근", "30605");
        cropMapping.put("두릅", "30606");
        cropMapping.put("딸기(사계성여름재배)", "30609");
        cropMapping.put("딸기(촉성재배)", "30610");
        cropMapping.put("마늘", "30611");
        cropMapping.put("마늘(잎마늘)", "30612");
        cropMapping.put("멜론", "30613");
        cropMapping.put("무", "30614");
        cropMapping.put("무(고랭지재배)", "30615");
        cropMapping.put("미나리", "30616");
        cropMapping.put("배추", "30618");
        cropMapping.put("배추(고랭지재배)", "30619");
        cropMapping.put("부추", "30620");
        cropMapping.put("브로콜리(녹색꽃양배추 고랭지재배)", "30621");
        cropMapping.put("브로콜리(평야지재배)", "30622");
        cropMapping.put("비트", "30623");
        cropMapping.put("상추", "30624");
        cropMapping.put("생강", "30625");
        cropMapping.put("셀러리(양미나리)", "30626");
        cropMapping.put("수박", "30627");
        cropMapping.put("시금치", "30628");
        cropMapping.put("신선초", "30629");
        cropMapping.put("쑥갓", "30630");
        cropMapping.put("아스파라거스", "30632");
        cropMapping.put("아욱", "30631");
        cropMapping.put("양배추", "30634");
        cropMapping.put("양파", "30633");
        cropMapping.put("연근", "30635");
        cropMapping.put("오이", "30636");
        cropMapping.put("적채", "30638");
        cropMapping.put("쪽파", "30639");
        cropMapping.put("참외", "30640");
        cropMapping.put("참취", "30641");
        cropMapping.put("청경채", "30643");
        cropMapping.put("치커리(쌈용 잎치커리)", "258609");
        cropMapping.put("치커리(치콘 뿌리치커리)", "30644");
        cropMapping.put("컬리플라워(백색꽃양배추 고랭지재배)", "258607");
        cropMapping.put("토란", "30645");
        cropMapping.put("토마토(방울토마토)", "30646");
        cropMapping.put("파", "30647");
        cropMapping.put("파드득나물", "258611");
        cropMapping.put("파슬리(향미나리)", "258608");
        cropMapping.put("파프리카", "30649");
        cropMapping.put("피망", "30650");
        cropMapping.put("호박", "30651");
        cropMapping.put("호박(늙은호박)", "30652");
        cropMapping.put("호박(단호박)", "30653");
        cropMapping.put("감귤(노지재배)", "30654");
        cropMapping.put("감귤(시설재배)", "30655");
        cropMapping.put("단감", "30656");
        cropMapping.put("매실", "30658");
        cropMapping.put("무화과(노지재배)", "30659");
        cropMapping.put("무화과(무가온 시설재배)", "30660");
        cropMapping.put("배", "30661");
        cropMapping.put("복숭아", "30662");
        cropMapping.put("블루베리", "258549");
        cropMapping.put("사과", "30663");
        cropMapping.put("살구", "30664");
        cropMapping.put("양앵두(체리)", "30665");
        cropMapping.put("유자", "30666");
        cropMapping.put("자두", "30667");
        cropMapping.put("참다래", "30668");
        cropMapping.put("포도(무가온)", "30669");
        cropMapping.put("포도(표준가온)", "258613");
        cropMapping.put("플럼코트", "258633");
        cropMapping.put("한라봉(부지화)", "30670");
        cropMapping.put("기계이앙재배", "30697");
        cropMapping.put("직파재배", "30698");
        cropMapping.put("감자", "30699");
        cropMapping.put("강낭콩", "30700");
        cropMapping.put("고구마", "30701");
        cropMapping.put("녹두", "30702");
        cropMapping.put("들깨(잎)", "30607");
        cropMapping.put("들깨(종실)", "30703");
        cropMapping.put("땅콩", "30704");
        cropMapping.put("맥주보리", "30705");
        cropMapping.put("메밀", "30706");
        cropMapping.put("밀", "30707");
        cropMapping.put("수수", "30708");
        cropMapping.put("옥수수", "30709");
        cropMapping.put("완두", "30710");
        cropMapping.put("유채", "30711");
        cropMapping.put("일반보리", "30712");
        cropMapping.put("조", "30713");
        cropMapping.put("참깨", "30714");
        cropMapping.put("콩", "30715");
        cropMapping.put("팥", "30716");
        cropMapping.put("풋콩", "30717");
        cropMapping.put("느타리버섯", "30733");
        cropMapping.put("양송이", "30735");
        cropMapping.put("영지버섯", "30734");
        cropMapping.put("팽이", "30736");
        cropMapping.put("구기자", "30739");
        cropMapping.put("길경(도라지)", "30740");
        cropMapping.put("더덕(양유)", "30741");
        cropMapping.put("두충", "30743");
        cropMapping.put("산약(마)", "30747");
        cropMapping.put("오미자", "30749");
        cropMapping.put("천마", "30756");
        cropMapping.put("황기", "30761");
    }

    
    public String getCropSchedule(String cropName) {
        String cntntsNo = cropMapping.get(cropName);
        if (cntntsNo == null) {
            return null; // 매핑 정보가 없는 경우
        }
        if (apiKey == null || apiKey.isBlank()) {
            return null;
        }
        
        String url = UriComponentsBuilder.fromHttpUrl(BASE_URL)
            .queryParam("cntntsNo", cntntsNo)
            .queryParam("apiKey", apiKey)
            .build()
            .encode()
            .toUriString();
        RestTemplate restTemplate = new RestTemplate();
        String xmlResponse = restTemplate.getForObject(url, String.class);
        
        // XML 파싱: <htmlCn> 태그의 텍스트(HTML 템플릿)를 추출
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            ByteArrayInputStream input = new ByteArrayInputStream(xmlResponse.getBytes("UTF-8"));
            Document doc = builder.parse(input);
            NodeList nodeList = doc.getElementsByTagName("htmlCn");
            if (nodeList.getLength() > 0) {
                Node htmlCnNode = nodeList.item(0);
                String htmlContent = htmlCnNode.getTextContent();
                return htmlContent;
            } else {
                return null;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
